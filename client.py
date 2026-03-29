import argparse
import webbrowser


def run_client(host, port):
	url = f"http://{host}:{port}"
	print(f"Opening browser: {url}")
	webbrowser.open(url)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Open the browser chat client")
	parser.add_argument("--host", default="localhost", help="Server host/IP")
	parser.add_argument("--port", type=int, default=8000, help="Server port")
	args = parser.parse_args()
	run_client(args.host, args.port)