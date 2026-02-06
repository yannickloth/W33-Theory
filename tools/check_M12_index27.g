G := AtlasGroup("M12");
Print("|G| = ", Size(G), "\n");
CC := ConjugacyClassesSubgroups(G);
Print("conjugacy classes of subgroups: ", Length(CC), "\n");
res := Filtered(CC, c -> Size(G) / Size(Representative(c)) = 27);
Print("found ", Length(res), " classes with index 27\n");
for c in res do
    H := Representative(c);
    Print("Index = ", Index(G,H), ", Size(H) = ", Size(H), ", Structure = ", StructureDescription(H), "\n");
od;

Quit();
