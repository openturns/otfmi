import pyAgrum as gum

gum.about()

bn=gum.fastBN("A->B<-C->D->A")
bn.saveBIF("one.bif")

bn2=gum.loadBN("one.bif")
bn2.saveDSL("two.dsl")

bn3=gum.loadBN("two.dsl")
bn3.saveNET("three.net")

bn4=gum.loadBN("three.net")

if bn==bn2:
    print("ok2")
if bn==bn3:
    print("ok3")
if bn==bn4:
    print("ok4")

bn5=gum.fastBN("A->B->C->D")
if bn==bn5:
    print("not ok5")
else:
    print("ok5")
