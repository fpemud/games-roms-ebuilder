prefix=/usr

all:

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/bin"
	for fn in src/*-ebuild ; do nfn=$(DESTDIR)/$(prefix)/bin/`basename $fn` ; sed -e '/##include-point##/{r common.py\nd}' $fn > $nfn ; chmod 755 $nfn ; done

.PHONY: all clean install
