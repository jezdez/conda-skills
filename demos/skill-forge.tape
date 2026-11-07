Set Height 600
Source demos/_settings.tape
Output demos/skill-forge.gif

Hide
Type `source demos/setup.sh author`
Enter
Wait /\$/
Type "clear"
Enter
Sleep 500ms
Show

Type `conda create -y -p ../skills --override-channels -c https://prefix.dev/skill-forge "agent-skill-polars==0.0.8"`
Enter
Wait /\$/
Sleep 2s
Type "conda activate ../skills"
Enter
Wait /\$/
Type "clear"
Enter
Type "conda skill list"
Enter
Wait /\$/
Sleep 2s
Type "# Review SKILL.md and supporting files before linking"
Enter
Type `bat --line-range 1:18 "$CONDA_PREFIX/share/agent-skills/polars/SKILL.md"`
Enter
Wait /\$/
Sleep 4s
Type "clear"
Enter
Type "conda skill link polars"
Enter
Wait /\$/
Type "conda skill status"
Enter
Wait /\$/
Sleep 3s
Type "conda skill unlink polars"
Enter
Wait /\$/
Sleep 2s
Type "conda deactivate"
Enter
Wait /\$/
Sleep 2s
