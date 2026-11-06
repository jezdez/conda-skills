Set Height 600
Source demos/_settings.tape
Output demos/recover-link.gif

Hide
Type `source demos/setup.sh installed`
Enter
Wait /\$/
Type "conda skill install review-notes -p ../skills"
Enter
Wait /\$/
Type "clear"
Enter
Sleep 500ms
Show

Type "# Simulate moving the source environment away"
Enter
Type "mv ../skills ../skills-moved"
Enter
Type "conda skill status"
Enter
Wait /\$/
Sleep 3s
Type "ls -ld .agents/skills/review-notes"
Enter
Wait /\$/
Sleep 2s
Type "# Remove only the inspected symlink, not its target directory"
Enter
Type "unlink .agents/skills/review-notes"
Enter
Type "conda skill install review-notes -p ../skills-moved"
Enter
Wait /\$/
Type "conda skill status"
Enter
Wait /\$/
Sleep 3s
