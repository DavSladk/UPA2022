.PHONY: pdf clean zip

pdf:
	pdflatex -output-directory doc doc/documentation.tex
	pdflatex -output-directory doc doc/documentation.tex

clean:
	rm -f doc/documentation.aux
	rm -f doc/documentation.log
	rm -f doc/documentation.out
	rm -f doc/documentation.toc
	rm -f xkolec08_xmorav41_xsladk07.zip

zip: clean
	zip -r xkolec08_xmorav41_xsladk07.zip app.py database.py download.py parser.py query.py Makefile README.md doc