Print("GAP version: "); Print(Version(), "\n");
G := AtlasGroup("M12");;
Print("Size(M12)=", Size(G), "\n");
Print("Degree(M12)=", DegreePermGroup(G), "\n");
H := AtlasGroup("2.M12");;
if H = fail then
  Print("2.M12 not available\n");
else
  Print("Size(2.M12)=", Size(H), "\n");
fi;
# Print generators of M12
Print("Generators of M12:\n");;
Print(GeneratorsOfGroup(G), "\n");
# Print group id
Print("IdGroup(M12)=", IdGroup(G), "\n");
