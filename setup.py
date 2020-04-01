import setuptools

with open('README.md', 'r') as fh:
	actual_description= fh.read()


	setuptools.setup(
	    name="timetester", 
	    version="1.1.1",
	    author="Matthew Lam",
	    author_email="lcpmatthew@gmail.com",
	    description="Python package to get an average time of your function",
	    long_description=actual_description,
	    long_description_content_type="text/markdown",
	    url="https://github.com/feimaomiao/timetester",
	    packages=setuptools.find_packages(),
	    install_requires=['matplotlib'],
	    classifiers=[
	        "Programming Language :: Python :: 3",
	        "License :: OSI Approved :: MIT License",
	        "Operating System :: OS Independent",
	    ],
	    python_requires='>=3.8',
	)