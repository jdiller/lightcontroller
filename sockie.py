import websocket
import thread
import time
import sys

websocket.enableTrace(True)

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "***CLOSED***"

def on_open(ws):
    def run(*args):
        try:
            while True:
                ws.send('beep');
                time.sleep(45)
        finally:
            ws.close()
    thread.start_new_thread(run, ())

while True:
    ws = websocket.WebSocketApp("ws://wf-lights-staging.herokuapp.com/listen",
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close
        )

    ws.on_open = on_open
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print "Exiting"
        sys.exit(0)


