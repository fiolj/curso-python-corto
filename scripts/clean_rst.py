from sys import argv
import re


def clean_images(Sin):
  pf = re.compile(r"\.\. (\|image[0-9]\|) image:: (.+\.png)")

  m = pf.search(Sin)
  while m is not None:
    s, e = m.span()               # start, end
    ref, figname = m.groups()
    fig = ".. image:: {}\n\n".format(figname)
    Sin = Sin[:s].replace(ref, fig) + Sin[e:]
    m = pf.search(Sin)

  return Sin


st = [r"({})".format("[-]{3,}"),      # separador   \1
      r"[ \n]*Ejercicios ",
      r"([0-9]{1,2})[ ]*",           # class number  \2
      r"(?:\([a-e]\))?\n",           # part in class (a), (b), ...
      r"(.)\3+\n",              # subrayado  \3
      r"(.*?)\n\n\1"            # texto de los ejercicios  \4
      ]

p1 = re.compile("".join(st), re.DOTALL | re.M)


def extract_ejerc(Sin):
  "Extrae los ejerciccios de las notebooks"
  cl = ""
  ejs = ""
  for m in p1.finditer(Sin):
    cl = m.groups()[1]
    text = m.groups()[-1]
    ejs += "{}\n".format(text)

  return cl, ejs


admonitions = [('Nota', 'note'), ('Advertencia', 'warning'), ('Consejo', 'hint'), ('Ejemplo', 'hint'),
               ('Truco', 'tip'), ('Importante', 'Important'), ('Atención', 'Attention')]
adm = {}
for a in admonitions:
  adm[a[1]] = a[0][0].upper() + ''.join('[{}{}]'.format(x.upper(), x.lower())
                                        for x in a[0][1:])


def modify_note(Sin):
  "Change the notes in markdown for notes in rst using roles"
  sep = "[-]{3,}"

  for k, v in adm.items():
    Sout = ""
    snota = r"\*\*{}:\*\*".format(v)
    rnota = ".. {}:: ".format(k)
    p1 = re.compile(
        "({0}[ \n]*{1})(.*?)({0})".format(sep, snota), re.DOTALL | re.M)
    ss = 0
    for mi in p1.finditer(Sin):
      s, e = mi.span()
      nota = mi.groups()[1].replace("\n", "\n  ")
      Sout += Sin[ss:s] + rnota + nota
      ss = e
    else:
      Sout += Sin[ss:]
    Sin = Sout
  return Sout


if __name__ == '__main__':

  fnames = argv[1:]
  for fname in fnames:
    with open(fname, 'r') as fi:
      S = fi.read()

    Sout = modify_note(S)

    with open(fname, 'w') as fo:
      fo.write(Sout)
