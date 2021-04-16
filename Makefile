CLSDIR:=./
MNDIR:=curso-python-corto
SRCDIR:=web/source/
STTDIR:=$(SRCDIR)_static/
RECDIR=web/recursos/
SCRIPT=scripts/create_index.py
EXTRASOURCES=index.rst 
RSTSOURCES= $(addprefix $(SRCDIR), $(EXTRASOURCES))
addit_estilos=$(STTDIR)/rtd_overrides.css $(STTDIR)/pygments.css
dataweb= $(SRCDIR)/figuras $(SRCDIR)/data


# ----------------------------------------------------------------------
# Agregar aqui las fuentes de las clases
CLSSRC= $(CLSDIR)00_instala_y_uso.ipynb 01_introd_python.ipynb

CLSRST=$(SRCDIR)/clase_00.rst $(SRCDIR)/clase_01.rst  $(SRCDIR)/clase_02.rst

$(SRCDIR)/clase_00.rst: $(CLSDIR)/00_instala_y_uso.ipynb
	@echo "--- Preparando clases: 00 ---"
	@$(SCRIPT) -c 00 $^
	mv clase_00.rst $(SRCDIR)

$(SRCDIR)/clase_01.rst: $(CLSDIR)/01_introd_python.ipynb
	@echo "--- Preparando clases: 01 ---"
	@$(SCRIPT) -c 01 $^
	mv clase_01.rst $(SRCDIR)

$(SRCDIR)/clase_02.rst: $(CLSDIR)/02_introd_cientif.ipynb
	@echo "--- Preparando clases: 02 ---"
	@$(SCRIPT) -c 02 $^
	mv clase_02.rst $(SRCDIR)


# ----------------------------------------------------------------------

SOURCES= $(CLSRST) $(EJRST) $(RSTSOURCES)

conf:
	cp -u $(RECDIR)conf.py $(SRCDIR)

.PHONY: clean-all clean depends html pdf publish conf


$(SRCDIR)%.rst: $(CLSDIR)%.rst
	cp $^ $@

logos:
	cp -u $(RECDIR)images/* $(STTDIR)


html: $(SOURCES) $(dataweb) $(addit_estilos) logos conf
	cp -ruv figuras data $(SRCDIR)
	cd web; make html; cp -ruv source/figuras/*.* build/html/_images

pdf: web/build/latex/ClasesdePython.pdf conf

web/build/latex/ClasesdePython.pdf:  $(SOURCES) $(dataweb) $(addit_estilos)
	@echo "SOURCES:" $(SOURCES)
	cp -ruv figuras data $(SRCDIR)
	cd web; make latex; cd build/latex; xelatex ClasesdePython.tex; xelatex ClasesdePython.tex

$(addit_estilos): $(subst $(STTDIR)/,$(RECDIR)styles/,$(addit_estilos))
	cp $^ $(STTDIR)/


publish: html
	rsync -rv --delete --exclude=".nojekyll" web/build/html/ ../$(MNDIR)/docs/
	# rsync -ruv  web/build/latex/ClasesdePython.pdf $(HOME)/Trabajos/fiolj.io/data/


clean-docs:
	cd web && make clean; cd -
	rm web/source/*.rst

clean: clean-docs

clean-all: clean-docs


