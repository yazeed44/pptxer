rm -rf dist/ src/pptxer.egg-info/ && python3 -m build \
&& python3 -m twine upload --repository $1 dist/*