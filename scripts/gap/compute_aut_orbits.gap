F := GF(3);
P := [ [0,1,1,1,1,1], [1,0,1,2,2,1], [1,1,0,1,2,2], [1,2,1,0,1,2], [1,2,2,1,0,1], [1,1,2,2,1,0] ];
I := IdentityMat(6,F);
Grows := List([1..6], i -> Concatenation(I[i], P[i]));
Gmat := Matrix(F, Grows);

# Generate all 3^6 codewords
Cwords := [];
for a0 in [0..2] do
  for a1 in [0..2] do
    for a2 in [0..2] do
      for a3 in [0..2] do
        for a4 in [0..2] do
          for a5 in [0..2] do
            v := [a0,a1,a2,a3,a4,a5];
            vec := Vector(F, v) * Gmat;
            cw := List([1..12], i -> Int(vec[i]));
            Add(Cwords, cw);
          od;
        od;
      od;
    od;
  od;
od;

len := Length(Cwords);
Print("Generated ", len, " codewords\n");

# Build map from codeword to index (1-based)
IndexMap := NewDictionary();
for i in [1..len] do
  key := String(Cwords[i]);
  IndexMap[key] := i;
od;

# Load M12 from AtlasRep
G := AtlasGroup("M12");;
Print("M12 size: ", Size(G), "\n");

# Function to apply permutation on coordinates
ApplyPermToCodeword := function(cw, perm)
  local res, i;
  res := [];
  for i in [1..12] do
    # image of i under perm
    img := Image(perm, i);
    Add(res, cw[img]);
  od;
  return res;
end;

# Build permutations on the 729 points induced by M12 generators
Perms := [];
for gen in GeneratorsOfGroup(G) do
  permList := [];
  for i in [1..len] do
    newcw := ApplyPermToCodeword(Cwords[i], gen);
    key := String(newcw);
    if not IsBound(IndexMap[key]) then
      Error("Permutation sends codeword outside the code (shouldn't happen)\n");
    fi;
    Add(permList, IndexMap[key]);
  od;
  p := PermList(permList);
  Add(Perms, p);
  Print("Added permutation from generator, cycle structure: ", CycleStructureString(p), "\n");
od;

# Add global negation as permutation (multiply codewords by 2 mod 3)
negList := [];
for i in [1..len] do
  cw := Cwords[i];
  neg := List(cw, x -> (2 * x) mod 3);
  key := String(neg);
  Add(negList, IndexMap[key]);
od;
negPerm := PermList(negList);
Print("Negation permutation cycle structure: ", CycleStructureString(negPerm), "\n");
Add(Perms, negPerm);

H := Group(Perms);
Print("Constructed group H with Size = ", Size(H), "\n");

# Orbits on all codewords
orbs := Orbits(H, [1..len]);
Print("Number of orbits on 729 codewords: ", Length(orbs), "\n");
# Print sizes of orbits sorted
sizes := SortedList(List(orbs, o -> Length(o)));
Print("Orbit sizes (sorted): ", sizes, "\n");

# Check for orbits of size 27
orbs27 := Filtered(orbs, o -> Length(o) = 27);
Print("Number of orbits of size 27: ", Length(orbs27), "\n");
if Length(orbs27) > 0 then
  Print("Sample orbit elements (indices): ", orbs27[1], "\n");
  # print the corresponding codewords
  Print("Sample codewords from sample orbit:\n");
  for idx in orbs27[1] do
    Print(Cwords[idx], "\n");
  od;
fi;

# Also check orbits on nonzero codewords only (exclude index of zero codeword)
zeroIdx := Position(Cwords, List([1..12], i -> 0));
nonzeroPts := Filtered([1..len], i -> i <> zeroIdx);
orbs_nonzero := Orbits(H, nonzeroPts);
Print("Orbits on nonzero codewords: ", Length(orbs_nonzero), "\n");
sizes_nz := SortedList(List(orbs_nonzero, o -> Length(o)));
Print("Orbit sizes on nonzero (sorted): ", sizes_nz, "\n");

# Consider projective classes (identify c with -c): create canonical representative index per class
projRep := [];
RepMap := NewDictionary();
visited := Set([]);
for i in nonzeroPts do
  if not i in visited then
    key := String(Cwords[i]);
    negkey := String(List(Cwords[i], x -> (2*x) mod 3));
    j := IndexMap[negkey];
    Add(visited, i);
    Add(visited, j);
    Add(projRep, i);
    RepMap[String(Cwords[i])] := i;
    RepMap[negkey] := i;
  fi;
od;
projSize := Length(projRep);
Print("Projective classes (nonzero)/2 size: ", projSize, " (should be 364)\n");

# Build action on projective classes: for each generator, map representative i to the representative of its image under perm
projPerms := [];
for p in Perms do
  projPermList := [];
  for r in projRep do
    imgIdx := Image(p, r);
    repOfImg := RepMap[String(Cwords[imgIdx])];
    Add(projPermList, repOfImg);
  od;
  Add(projPerms, PermList(projPermList));
od;
Hproj := Group(projPerms);
Print("Hproj size: ", Size(Hproj), "\n");
orbs_proj := Orbits(Hproj, projRep);
Print("Projective orbits count: ", Length(orbs_proj), "\n");
psizes := SortedList(List(orbs_proj, o -> Length(o)));
Print("Projective orbit sizes: ", psizes, "\n");
proj27 := Filtered(orbs_proj, o -> Length(o) = 27);
Print("Number of projective orbits of size 27: ", Length(proj27), "\n");
if Length(proj27) > 0 then
  Print("Sample projective orbit indices: ", proj27[1], "\n");
fi;
