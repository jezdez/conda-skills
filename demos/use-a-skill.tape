Source demos/_settings.tape
Output demos/use-a-skill.gif

Hide
Type `source demos/setup.sh installed`
Enter
Wait /\$/
Type "clear"
Enter
Sleep 500ms
Show

Type "# The example package is already installed in ../skills"
Enter
Type "conda skill list -p ../skills"
Enter
Wait /\$/
Sleep 2s
Type "# Read the instructions before making them available to an agent"
Enter
Type "bat ../skills/share/agent-skills/review-notes/SKILL.md"
Enter
Wait /\$/
Sleep 3s
Type "clear"
Enter
Sleep 500ms
Type "conda skill install review-notes -p ../skills"
Enter
Wait /\$/
Sleep 2s
Type "conda skill status"
Enter
Wait /\$/
Sleep 2s
Type "conda skill remove review-notes -p ../skills"
Enter
Wait /\$/
Sleep 2s
