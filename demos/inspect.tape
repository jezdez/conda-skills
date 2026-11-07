Set Height 800
Source demos/_settings.tape
Output demos/inspect.gif

Hide
Type `source demos/setup.sh installed`
Enter
Wait /\$/
Type "conda activate ../skills"
Enter
Wait /\$/
Type "clear"
Enter
Sleep 500ms
Show

Type "conda skill inspect review-notes"
Enter
Wait /\$/
Sleep 4s
Type "clear"
Enter
Type "conda skill inspect review-notes --file SKILL.md"
Enter
Wait /\$/
Sleep 5s
Type "clear"
Enter
Type "conda skill inspect review-notes --file references/checklist.md"
Enter
Wait /\$/
Sleep 4s
Type "# After reviewing the files:"
Enter
Type "conda skill link review-notes"
Enter
Wait /\$/
Sleep 3s
