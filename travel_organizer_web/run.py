from app import app_instance

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible from network, for local offline, '127.0.0.1' is fine.
    # debug=True is useful for development.
    app_instance.run(host='127.0.0.1', port=5000, debug=True)
