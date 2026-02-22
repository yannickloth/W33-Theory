G := AtlasGroup("2.M12");
Print("|G| = ", Size(G), "\n");
CC := ConjugacyClassesSubgroups(G);
Print("conjugacy classes of subgroups: ", Length(CC), "\n");
res := Filtered(CC, c -> Size(G) / Size(Representative(c)) = 27);
Print("found ", Length(res), " classes with index 27\n");
for c in res do
    H := Representative(c);
    Print("Index = ", Index(G,H), ", Size(H) = ", Size(H), ", Structure = ", StructureDescription(H), "\n");
od;

# Also list transitive permutation representations of small degree
# (try to find transitive subgroups or primitive action of degree 27)
PR := PossiblePermutationRepresentations(G, 27);
Print("Possible permutation representations of degree 27: ", Length(PR), "\n");
for r in PR do
    Print(r, "\n");
od;

Quit();
