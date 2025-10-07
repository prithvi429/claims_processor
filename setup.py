from setuptools import setup, find_packages

setup(
    name="claims_processor",
    version="0.1.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'pytesseract', 'pdfplumber', 'pdf2image', 'pillow', 'spacy', 'openai'
    ],
)
