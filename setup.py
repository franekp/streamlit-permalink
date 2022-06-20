from setuptools import setup


setup(
    name='streamlit-permalink',
    version='0.1.0',
    description='Effortless permalinks in Streamlit apps.',
    long_description='Effortless permalinks in Streamlit apps.',
    author='Franciszek Piszcz',
    author_email='franciszek.piszcz@rtbhouse.com',
    url='https://github.com/franekp/streamlit-permalink',
    py_modules=['streamlit_permalink'],
    install_requires=[
        'streamlit >= 1.4.0',
    ],
)
