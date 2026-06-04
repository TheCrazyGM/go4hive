/**
 * Go4Hive - Terminal & Command Console Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const cmdInput = document.getElementById('cmd-input');
    const terminalMsg = document.getElementById('terminal-msg');
    const allLinks = Array.from(document.querySelectorAll('body a:not(#retro-modal a)'));

    // CURRENT_USER is expected to be defined globally in the template
    const user = window.HIVE_USER || '';

    let selectedIndex = -1;
    let msgTimeout = null;

    // --- System Notifications ---
    window.printMsg = function(msg, isError = false) {
        if (msgTimeout) clearTimeout(msgTimeout);

        terminalMsg.innerText = msg;
        terminalMsg.style.display = 'block';
        terminalMsg.style.color = isError ? '#ff0000' : 'var(--text-color)';

        msgTimeout = setTimeout(() => {
            terminalMsg.style.display = 'none';
        }, 5000);
    };

    // --- Keyboard Cursor Logic ---
    function updateCursor(newIndex, scroll = true) {
        if (allLinks.length === 0) return;

        if (selectedIndex >= 0 && allLinks[selectedIndex]) {
            allLinks[selectedIndex].classList.remove('terminal-cursor');
        }

        selectedIndex = Math.max(0, Math.min(newIndex, allLinks.length - 1));
        const selected = allLinks[selectedIndex];
        selected.classList.add('terminal-cursor');

        if (scroll) {
            selected.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    if (allLinks.length > 0) {
        updateCursor(0, false);
    }

    // --- Argument Parsing (Shell-style) ---
    function parseArgs(input) {
        const args = [];
        let current = '';
        let inQuotes = false;
        let quoteChar = '';

        for (let i = 0; i < input.length; i++) {
            const char = input[i];
            if ((char === '"' || char === "'") && (i === 0 || input[i-1] !== '\\')) {
                if (inQuotes && char === quoteChar) {
                    inQuotes = false;
                    args.push(current);
                    current = '';
                } else if (!inQuotes) {
                    inQuotes = true;
                    quoteChar = char;
                } else {
                    current += char;
                }
            } else if (char === ' ' && !inQuotes) {
                if (current.length > 0) {
                    args.push(current);
                    current = '';
                }
            } else {
                current += char;
            }
        }
        if (current.length > 0) args.push(current);
        return args;
    }

    // --- Command Execution ---
    function executeCommand(rawCmd) {
        const parts = parseArgs(rawCmd.trim());
        if (parts.length === 0) return;

        const command = parts[0].toLowerCase();
        const args = parts.slice(1);

        switch(command) {
            case 'login':
                if (!args[0]) {
                    printMsg('USAGE: login <username>', true);
                    return;
                }
                handleLogin(args[0]);
                break;
            case 'logout':
                window.location.href = '/logout/';
                break;
            case 'home':
            case 'h':
                window.location.href = '/';
                break;
            case 'trending':
                window.location.href = '/trending/';
                break;
            case 'hot':
                window.location.href = '/hot/';
                break;
            case 'feed':
                if (!user) {
                    printMsg('HANDSHAKE REQUIRED. PLEASE LOGIN FIRST.', true);
                    return;
                }
                window.location.href = '/feed/';
                break;
            case 'search':
                window.location.href = '/search/';
                break;
            case 'witness':
            case 'witnesses':
                window.location.href = '/witnesses/';
                break;
            case 'blocks':
                window.location.href = '/blocks/';
                break;
            case 'market':
                window.location.href = '/market/';
                break;
            case 'wallet':
                if (args[0]) {
                    window.location.href = `/wallet/${args[0].replace('@', '')}/`;
                } else if (user) {
                    window.location.href = '/wallet/';
                } else {
                    printMsg('HANDSHAKE REQUIRED OR PROVIDE USERNAME: wallet <user>', true);
                }
                break;
            case 'post':
                if (!user) {
                    printMsg('HANDSHAKE REQUIRED. PLEASE LOGIN FIRST.', true);
                    return;
                }
                const initialTag = args[0] || '';
                window.location.href = `/editor/?tag=${encodeURIComponent(initialTag)}`;
                break;
            case 'help':
                window.location.href = '/help/';
                break;
            case 'vote':
                if (!user) {
                    printMsg('HANDSHAKE REQUIRED. PLEASE LOGIN FIRST.', true);
                    return;
                }
                handleVote(args[0]);
                break;
            case 'transfer':
                if (!user) {
                    printMsg('HANDSHAKE REQUIRED. PLEASE LOGIN FIRST.', true);
                    return;
                }
                if (args.length < 2) {
                    printMsg('USAGE: transfer <to> <amount> [currency] [memo]', true);
                    return;
                }
                handleTransfer(args);
                break;
            default:
                printMsg(`UNKNOWN COMMAND: ${command}`, true);
        }
    }

    // --- Keychain Handlers ---
    function handleLogin(username) {
        if (!window.hive_keychain) {
            printMsg('HIVE KEYCHAIN EXTENSION NOT FOUND.', true);
            return;
        }
        const cleanUser = username.replace('@', '');
        const message = 'Go4Hive Login Handshake';
        printMsg(`AWAITING HANDSHAKE FROM @${cleanUser}...`);
        window.hive_keychain.requestSignBuffer(cleanUser, message, 'Posting', (response) => {
            if (response.success) {
                printMsg('SIGNATURE GENERATED. VERIFYING ON SERVER...');

                // POST the signature and buffer to the server for verification
                fetch(`/login-handshake/${cleanUser}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        signature: response.result,
                        buffer: message,
                        publicKey: response.publicKey
                    })
                }).then(res => {
                    if (res.ok) {
                        printMsg('SIGNATURE VERIFIED. REDIRECTING...');
                        window.location.href = '/';
                    } else {
                        res.text().then(text => {
                            printMsg(`SERVER VERIFICATION FAILED: ${text}`, true);
                        });
                    }
                }).catch(err => {
                    printMsg('COMMUNICATION ERROR DURING HANDSHAKE.', true);
                });
            } else {
                printMsg(`LOGIN FAILED: ${response.message}`, true);
            }
        });
    }

    function handleVote(weight) {
        const postHeader = document.querySelector('.post-header');
        if (!postHeader) {
            printMsg('ERROR: VOTE COMMAND ONLY VALID INSIDE POST DETAIL VIEW.', true);
            return;
        }
        if (!window.hive_keychain) {
            printMsg('HIVE KEYCHAIN EXTENSION NOT FOUND.', true);
            return;
        }
        const author = postHeader.getAttribute('data-author');
        const permlink = postHeader.getAttribute('data-permlink');
        const voteWeight = parseInt(weight || '100') * 100;
        printMsg(`INITIATING VOTE FOR @${author}...`);
        window.hive_keychain.requestVote(user, permlink, author, voteWeight, (response) => {
            if (response.success) {
                printMsg(`SUCCESS: BROADCASTED ${weight || '100'}% VOTE.`);
            } else {
                printMsg(`VOTE FAILED: ${response.message}`, true);
            }
        });
    }

    function handleTransfer(args) {
        if (!window.hive_keychain) {
            printMsg('HIVE KEYCHAIN EXTENSION NOT FOUND.', true);
            return;
        }
        const to = args[0].replace('@', '');
        let rawAmount = args[1];
        let currency = 'HIVE';
        let memo = '';

        if (args[2] && ['HIVE', 'HBD'].includes(args[2].toUpperCase())) {
            currency = args[2].toUpperCase();
            memo = args.slice(3).join(' ');
        } else {
            memo = args.slice(2).join(' ');
        }

        const parsedAmount = parseFloat(rawAmount);
        if (isNaN(parsedAmount)) {
            printMsg(`INVALID AMOUNT: ${rawAmount}`, true);
            return;
        }
        const amount = parsedAmount.toFixed(3);
        currency = currency.toUpperCase();
        memo = memo.replace(/^["']|["']$/g, '');

        printMsg(`INITIATING TRANSFER OF ${amount} ${currency} TO @${to}...`);
        window.hive_keychain.requestTransfer(user, to, amount, memo, currency, (response) => {
            if (response.success) {
                printMsg(`SUCCESS: TRANSFERRED ${amount} ${currency} TO @${to}.`);
            } else {
                printMsg(`TRANSFER FAILED: ${response.message}`, true);
            }
        });
    }

    // --- Global Key Listener ---
    document.addEventListener('keydown', (e) => {
        const retroModal = document.getElementById('retro-modal');
        if (retroModal && retroModal.style.display === 'flex') {
            if (e.key === 'Escape') {
                e.preventDefault();
                closeVoteModal();
            }
            return;
        }

        if (document.activeElement !== cmdInput && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {

            if (e.key === ':' || e.key === '/') {
                e.preventDefault();
                cmdInput.focus();
                return;
            }

            if (e.key >= '0' && e.key <= '9') {
                const shortcut = document.querySelector(`[data-key="${e.key}"]`);
                if (shortcut) {
                    e.preventDefault();
                    shortcut.click();
                }
                return;
            }

            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    updateCursor(selectedIndex + 1, true);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    updateCursor(selectedIndex - 1, true);
                    break;
                case 'ArrowLeft':
                    history.back();
                    break;
                case 'ArrowRight':
                    history.forward();
                    break;
                case 'Enter':
                    if (selectedIndex >= 0 && allLinks[selectedIndex]) {
                        allLinks[selectedIndex].click();
                    }
                    break;
                case 'h':
                case 'H':
                    window.location.href = '/';
                    break;
            }
        } else if (document.activeElement === cmdInput) {
            if (e.key === 'Enter') {
                const cmd = cmdInput.value;
                cmdInput.value = '';
                cmdInput.blur();
                executeCommand(cmd);
            } else if (e.key === 'Escape') {
                cmdInput.blur();
            }
        }
    });

    // --- Retro Vote Modal Controller ---
    const retroModal = document.getElementById('retro-modal');
    const modalTarget = document.getElementById('modal-target');
    const modalWeight = document.getElementById('modal-weight');
    const modalSubmit = document.getElementById('modal-submit');
    const modalCancel = document.getElementById('modal-cancel');

    let currentVoteTarget = null;

    window.openVoteModal = function(author, permlink) {
        if (!user) {
            printMsg('ERROR: YOU MUST LOG IN TO VOTE.', true);
            return;
        }
        if (!window.hive_keychain) {
            printMsg('HIVE KEYCHAIN EXTENSION NOT FOUND.', true);
            return;
        }
        currentVoteTarget = { author, permlink };
        modalTarget.innerText = `@${author}`;
        modalWeight.value = '100';
        retroModal.style.display = 'flex';
        modalWeight.focus();
        modalWeight.select();
    };

    window.closeVoteModal = function() {
        if (retroModal) {
            retroModal.style.display = 'none';
        }
        currentVoteTarget = null;
    };

    function submitVoteModal() {
        if (!currentVoteTarget) return;
        const weightInput = modalWeight.value;
        const parsedWeight = parseInt(weightInput);
        if (isNaN(parsedWeight) || parsedWeight < 1 || parsedWeight > 100) {
            printMsg('ERROR: INVALID VOTE WEIGHT. MUST BE BETWEEN 1 AND 100.', true);
            return;
        }
        const { author, permlink } = currentVoteTarget;
        const voteWeight = parsedWeight * 100;

        closeVoteModal();
        printMsg(`INITIATING VOTE FOR @${author}...`);
        window.hive_keychain.requestVote(user, permlink, author, voteWeight, (response) => {
            if (response.success) {
                printMsg(`SUCCESS: BROADCASTED ${parsedWeight}% VOTE.`);
            } else {
                printMsg(`VOTE FAILED: ${response.message}`, true);
            }
        });
    }

    if (modalSubmit) {
        modalSubmit.addEventListener('click', (e) => {
            e.preventDefault();
            submitVoteModal();
        });
    }
    if (modalCancel) {
        modalCancel.addEventListener('click', (e) => {
            e.preventDefault();
            closeVoteModal();
        });
    }

    if (modalWeight) {
        modalWeight.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                submitVoteModal();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                closeVoteModal();
            }
        });
    }

    document.addEventListener('click', (e) => {
        const voteLink = e.target.closest('.vote-link');
        if (voteLink) {
            e.preventDefault();
            const author = voteLink.getAttribute('data-author');
            const permlink = voteLink.getAttribute('data-permlink');
            openVoteModal(author, permlink);
        }
    });
});
