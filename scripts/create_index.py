#! /usr/bin/env python3

from os import rename, remove
import os.path as osp
import argparse
import subprocess as sub
import re
from clean_rst import modify_note, clean_images, extract_ejerc

ultima = 0

clspath = "./"
webpath = "./"
indexfile = osp.join(webpath, 'index.rst')
ejercfile = osp.join(webpath, 'ejercicios.rst')

pf = re.compile(r"\.\. image:: ([0-1][0-9]_[^/]+)/(.+\.png)")


def create_rst(fuentes, cl):
  "Create clases in rst format from one of more notebooks per clase"
  nbs = [c for c in fuentes if "{:02d}".format(cl) in c]
  rts = [c.replace('ipynb', 'rst') for c in nbs]

  for nb in nbs:
    ret = convert_to_rst(nb)
    if ret != 0:
      print("Error creando {}".format(nb))
      return ret

  s = merge_clase(rts, cl)
  cle, ejs = extract_ejerc(s)

  with open("{}/clase_{:02d}.rst".format(webpath, cl), 'w') as fo:
    fo.write(s)

  if int(cl) != cl:
    print(cl, '!=', cle)

  if cle.strip() != '':
    ejfile = "ejercicios_{:02d}.rst".format(cl)
    # Escribe el archivo de ejercicios
    s = "Ejercicios de Clase {:02d}\n{}\n\n".format(cl, 22 * '-')
    with open("{}/{}".format(webpath, ejfile), 'w') as fo:
      fo.write(s + ejs)

    if osp.exists(ejercfile):
      with open(ejercfile, 'r') as fi:
        lines = fi.readlines()
    else:
      lines = []

    nlines = [l for l in lines if ".. include" in l]
    nej = ".. include:: {}\n".format(ejfile)
    if nej not in nlines:
      nlines.append(nej)

    # unique and sorted
    nlines = sorted(list(set(nlines)))

    s = """
**********
Ejercicios
**********

"""
    with open(ejercfile, 'w') as fo:
      fo.write(s + "".join(nlines))

  # for n, r in zip(nbs, rts):
  #   if n != r:
  #     remove(r)


def convert_to_rst(notebook):
  "Convert to rst by invoking jupyter"
  if osp.exists(notebook):
    if notebook.endswith('ipynb'):
      command = "jupyter nbconvert --to rst " + notebook
      return sub.call(command, shell=True, stdout=sub.PIPE)
    elif notebook.endswith('txt'):
      rename(notebook, notebook.replace('txt', 'rst'))
    elif notebook.endswith('rst'):
      return 0
  else:
    return -1


def change_code_to_python(Sin):
  "Change the code blocks from ipython3 to python"
  return Sin.replace(".. code:: ipython3", ".. code:: python")


def process_rst(Sin):
  "Fix the rst files"
  Sout = change_code_to_python(Sin)
  Sout = restore_figures(Sout)
  Sout = clean_images(Sout)
  Sout = modify_note(Sout)
  return Sout


def restore_figures(Sin):
  "Fix the path to the figures"
  for m in pf.finditer(Sin):
    d, f = m.groups()
    rename("{}/{}".format(d, f), "figuras/{}".format(f))
    Sin = Sin.replace(m.group(), ".. image:: figuras/{}".format(f))
  return Sin


def merge_clase(notebooks, clase):
  """
  notebooks: Lista con nombres de notebooks
  """

  # First notebook, add title
  with open(notebooks[0], 'r') as fi:
    l1 = fi.readline()           # read first line
    label = ".. _clase_{0:02d}:\n\n".format(clase)
    title = "Clase {0}: {1}".format(clase, l1)
    # read type of heading (if it is: =,-,~, etc)
    sub = fi.readline().strip()[0]
    subrayado = len(title) * sub + '\n'
    s = label + title + subrayado + "\n"
    s = s + process_rst(fi.read()) + '\n\n'

  # Rest of the files
  for fni in notebooks[1:]:
    with open(fni, 'r') as fi:
      s1 = fi.read()
      s += process_rst(s1)

  return s


def create_indexfile(nbs):
  indent = "\n   "

  deps = sort_dependencies(nbs)
  with open(osp.join(clspath, 'index.rst.tmpl'), 'r') as fi:
    template = fi.read()
  cls = ""                      # Clases
  # ejs = ""                      # Ejercicios
  # app = ""                      # Apéndices
  for n, d in deps.items():
    cls += indent + osp.splitext(osp.basename(d['clase']))[0]
    # if 'ejerc' in d:

  # for
  #   ejs += ".. include:: {}\n".format(osp.basename(d['ejerc'][0]))

  with open(indexfile, 'w') as fo:
    fo.write(template.format(cls))

#   s = """
# **********
# Ejercicios
# **********

# {}
# """
#   with open(ejercfile, 'w') as fo:
#     fo.write(s.format(ejs))


def sort_dependencies(docs):
  "busca qué nbs corresponden a qué clase"
  allnames = [osp.splitext(osp.split(c)[-1])[0] for c in docs]
  allnumeros = sorted(list({x.split("_")[0]
                            for x in allnames if x.split("_")[0].isdigit()}))
  deps = {}
  for n in allnumeros:
    nbs = [nb for nb in docs if "{}_".format(n) in nb]  # input notebooks y rst
    clase = "{}/clase_{}.rst".format(webpath, n)        # clase rst

    deps[n] = {'nbs': nbs, 'clase': clase}
  return deps


def create_dependencies(docs, fout="scripts/rstdeps.mk"):
  "Crea las dependencias de cada clase en los docs originales"
  deps = sort_dependencies(docs)

  # EJRST = "EJRST="  # Variable
  CLSRST = "CLSRST="  # Variable
  s = ""
  for n, d in deps.items():
    clase = d['clase']
    nbs = d['nbs']

    CLSRST += clase + " "
    s += "{}: {}\n".format(clase, " ".join(nbs))
    s += '\t@echo "--- Preparando clases: {} ---"\n'.format(n)
    s += "\t@$(SCRIPT) -c {} $^\n\n".format(n)

  s = CLSRST + 2 * '\n' + s
  if fout is not None:
    with open(fout, 'w') as fo:
      fo.write(s)
  return s


# def make_dependencies(docs, fout="scripts/rstdeps.mk"):
#   "Crea las dependencias de cada clase en los docs originales"
#   allnames = [osp.splitext(osp.split(c)[-1])[0] for c in docs]
#   allnumeros = sorted(list({x.split("_")[0]
#                             for x in allnames if x.split("_")[0].isdigit()}))

#   # EJRST = "EJRST="  # Variable
#   CLSRST = "CLSRST="  # Variable
#   s = ""
#   for n in allnumeros:
#     nbs = [nb for nb in docs if "{}_".format(n) in nb]
#     clase = "{}/clase_{}.rst".format(webpath, n)
#     CLSRST += clase + " "
#     s += "{}: {}\n".format(clase, " ".join(nbs))
#     s += '\t@echo "--- Preparando clases: {} ---"\n'.format(n)
#     s += "\t@$(SCRIPT) -c {} $^\n\n".format(n)
#     ejerc = "{}/{}_ejercicios.ipynb".format(clspath, n)
#     # print(ejerc, osp.exists(ejerc))
#     if osp.exists(ejerc):
#       ejrst = "{}/ejercicios_{}.rst".format(webpath, n)
#       s += "{}: {}\n".format(ejrst, ejerc)
#       EJRST += ejrst + " "
#       s += "\t@$(SCRIPT) -e {} $^\n\n".format(n)

#   s = CLSRST + 2 * '\n' + EJRST + 2 * '\n' + s
#   if fout is not None:
#     with open(fout, 'w') as fo:
#       fo.write(s)
#   return s


def main():
  parser = argparse.ArgumentParser(description='":Descripcion"')
  parser.add_argument('files', metavar='File', nargs='+',
                      help='Files to process (data accumulates)')
  parser.add_argument(
      "-o", "--output", default='-', metavar="file",
      help="Output file. Use '-' for stdout (screen)")
  parser.add_argument('-l', action="store_true", default=False,
                      help='Output clases involucradas')

  parser.add_argument('-c', action="append", dest="c", type=int,
                      help="Clase a procesar")

  parser.add_argument('-e', action="append", dest="e", type=int,
                      help="Ejercicio a procesar")

  parser.add_argument('-d', "--depends", action="store_true", dest="d",
                      help="Crea las dpendencias para todas las clases")

  parser.add_argument('-i', "--index", action="store_true", dest="i",
                      help="Write the index file")

  parser.add_argument('-n', action="store_true", default=False,
                      help='Output números de las clases involucradas')

  args = parser.parse_args()

  srcclases = args.files

  allnames = [osp.splitext(osp.split(c)[-1])[0] for c in srcclases]
  allnumeros = sorted(list({x.split("_")[0]
                            for x in allnames if x.split("_")[0].isdigit()}))
  allclases = ["clase_{}.rst".format(n) for n in allnumeros]

  if args.n:
    print(" ".join(allnumeros))
    return args.n

  if args.l:
    print(" ".join(allclases))
    return args.l

  if args.d:
    create_dependencies(srcclases)
    return True

  if args.c is not None:
    for cl in args.c:
      create_rst(srcclases, cl)

  if args.i:
    create_indexfile(srcclases)


if __name__ == "__main__":
  main()
