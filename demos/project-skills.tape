Set Height 600
Source demos/_settings.tape
Output demos/project-skills.gif

Hide
Type `source demos/setup.sh workspace`
Enter
Wait /\$/
Type "clear"
Enter
Sleep 500ms
Show

Type "bat conda.toml"
Enter
Wait /\$/
Sleep 3s
Type "conda workspace lock"
Enter
Wait /\$/
Sleep 2s
Type "conda workspace install --locked -e skills"
Enter
Wait /\$/
Sleep 2s
Type "clear"
Enter
Type "conda skill list -p .conda/envs/skills"
Enter
Wait /\$/
Sleep 2s
Type "# After reviewing the skill files:"
Enter
Type "clear"
Enter
Type "conda skill link polars -p .conda/envs/skills"
Enter
Wait /\$/
Type "conda skill status"
Enter
Wait /\$/
Sleep 3s
