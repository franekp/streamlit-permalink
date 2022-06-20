from setuptools import setup
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='streamlit-permalink',
    version='0.1.0',
    description='Effortless permalinks in Streamlit apps.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Franciszek Piszcz',
    author_email='franciszek.piszcz@rtbhouse.com',
    url='https://github.com/franekp/streamlit-permalink',
    py_modules=['streamlit_permalink'],
    install_requires=[
        'streamlit >= 1.4.0',
    ],
)
