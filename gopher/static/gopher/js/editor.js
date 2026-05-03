/**
 * Go4Hive - Post Editor Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const titleInput = document.getElementById('post-title');
    const tagsInput = document.getElementById('post-tags');
    const bodyInput = document.getElementById('post-body');
    const bufferStatus = document.getElementById('buffer-status');

    // HIVE_USER is expected to be defined globally
    const user = window.HIVE_USER || '';

    // --- Buffer Recovery ---
    const savedBody = localStorage.getItem('gopher_editor_body');
    if (savedBody) {
        bodyInput.value = savedBody;
        if (bufferStatus) bufferStatus.innerText = 'RECOVERED';
    }

    bodyInput.addEventListener('input', () => {
        localStorage.setItem('gopher_editor_body', bodyInput.value);
        if (bufferStatus) bufferStatus.innerText = 'MODIFIED';
    });

    // --- Broadcast Execution ---
    function doBroadcast() {
        if (!titleInput.value || !bodyInput.value) {
            if (window.printMsg) window.printMsg('ERROR: TITLE AND BODY ARE REQUIRED.', true);
            else alert('ERROR: TITLE AND BODY ARE REQUIRED.');
            return;
        }

        if (!window.hive_keychain) {
            if (window.printMsg) window.printMsg('HIVE KEYCHAIN NOT FOUND.', true);
            else alert('HIVE KEYCHAIN NOT FOUND.');
            return;
        }

        const title = titleInput.value;
        const body = bodyInput.value;
        const tags = tagsInput.value.toLowerCase().split(' ').filter(t => t.length > 0);

        // Per Hive standards, first tag is the primary category
        const parent_permlink = tags.length > 0 ? tags[0] : 'hive-100421';
        const permlink = title.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 255);

        if (bufferStatus) bufferStatus.innerText = 'BROADCASTING...';
        if (window.printMsg) window.printMsg('COMMUNICATING WITH MAINFRAME...');

        window.hive_keychain.requestPost(user, title, body, parent_permlink, '',
            JSON.stringify({tags: tags, app: 'go4hive/0.2.0'}), permlink, '', (response) => {
                if (response.success) {
                    if (bufferStatus) bufferStatus.innerText = 'SUCCESS';
                    localStorage.removeItem('gopher_editor_body');
                    if (window.printMsg) window.printMsg('SUCCESS: POST BROADCASTED TO HIVE!');
                    setTimeout(() => {
                        window.location.href = `/user/${user}/`;
                    }, 2000);
                } else {
                    if (bufferStatus) bufferStatus.innerText = 'FAILED';
                    if (window.printMsg) window.printMsg('BROADCAST FAILED: ' + response.message, true);
                    else alert('BROADCAST FAILED: ' + response.message);
                }
            });
    }

    // --- Editor Shortcuts ---
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey) {
            const key = e.key.toLowerCase();
            if (key === 'o') {
                e.preventDefault();
                doBroadcast();
            } else if (key === 'x') {
                e.preventDefault();
                if (bodyInput.value && !confirm('DISCARD CHANGES AND EXIT?')) return;
                localStorage.removeItem('gopher_editor_body');
                window.location.href = '/';
            } else if (key === 'k') {
                e.preventDefault();
                if (confirm('CLEAR ENTIRE BUFFER?')) {
                    bodyInput.value = '';
                    localStorage.removeItem('gopher_editor_body');
                    if (bufferStatus) bufferStatus.innerText = 'CLEAN';
                }
            } else if (key === 'g') {
                e.preventDefault();
                if (window.printMsg) {
                    window.printMsg('^O: Broadcast | ^X: Exit | ^K: Clear | TAB: Switch fields');
                } else {
                    alert('GO4HIVE NANO EDITOR\n^O: Broadcast\n^X: Exit\n^K: Clear\nUse TAB to switch fields.');
                }
            }
        }
    });
});
