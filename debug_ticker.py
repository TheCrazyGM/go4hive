from nectar.market import Market
import traceback


def debug_ticker():
    print("--- DEBUGGING MARKET TICKER ---")
    try:
        m = Market("HIVE:HBD")
        ticker = m.ticker()
        print("TICKER DATA RECEIVED:")
        print(ticker)

        if isinstance(ticker, dict):
            print(f"Latest: {ticker.get('latest')}")
        else:
            print(f"Ticker is not a dict, it is: {type(ticker)}")

    except Exception as e:
        print(f"TICKER FAILED: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    debug_ticker()
