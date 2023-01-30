import os


# get project root
root = os.path.dirname(os.path.abspath(__file__))

# add project root to PYTHONPATH
python_path = os.environ.get('PYTHONPATH', None)
if python_path is None:
    python_path = root
else:
    python_path = f'{root}:{python_path}'
os.environ['PYTHONPATH'] = python_path

from front_end.app import App


def main():
    fluxus_ai_app = App()
    fluxus_ai_app.run()


if __name__ == '__main__':
    main()
