from app import create_app

def main():
    try:
        app = create_app()
        print('APP_CREATED' if app else 'APP_FAIL')
    except Exception as e:
        print('APP_IMPORT_ERROR')
        print(e)

if __name__ == '__main__':
    main()
