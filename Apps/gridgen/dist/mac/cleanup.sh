cat ignore | while read dir; do
  rm -rf $dir
done

rm *.zip
rm *.dmg
