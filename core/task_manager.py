import threading

def run_in_thread(target, args):
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()