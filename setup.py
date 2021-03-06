import setuptools

setuptools.setup(
    name="zebr0-script",
    version="0.8.0",
    description="Minimalist local deployment based on zebr0 key-value system",
    long_description="TODO",
    long_description_content_type="text/markdown",
    author="Thomas JOUANNOT",
    author_email="mazerty@gmail.com",
    url="https://zebr0.io",
    download_url="https://github.com/zebr0/zebr0-script",
    packages=["zebr0_script"],
    scripts=["zebr0-script"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: System"
    ],
    license="MIT",
    install_requires=[
        "zebr0",
        "PyYAML"
    ]
)
