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
Type "clear"
Enter
Type "conda skill list -p ../skills"
Enter
Wait /\$/
Sleep 2s
Type "# Review SKILL.md and supporting files before installing a link"
Enter
Type "bat --line-range 1:18 ../skills/share/agent-skills/polars/SKILL.md"
Enter
Wait /\$/
Sleep 4s
Type "clear"
Enter
Type "conda skill install polars -p ../skills"
Enter
Wait /\$/
Type "conda skill status"
Enter
Wait /\$/
Sleep 3s
Type "conda skill remove polars -p ../skills"
Enter
Wait /\$/
Sleep 2s
