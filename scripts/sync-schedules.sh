#!/bin/zsh
# Make launchd match schedules/*.plist (the repo is the source of truth).
# Installs/updates every plist in schedules/, removes com.nick.miniheroes-* jobs that are no longer in the repo,
# then prints the current schedule. Re-run after editing/adding/deleting a file in schedules/.
REPO=${0:A:h:h}; LA=~/Library/LaunchAgents; U=gui/$(id -u)
for p in $REPO/schedules/*.plist(N); do
  l=${p:t:r}
  if ! cmp -s $p $LA/${p:t}; then
    launchctl bootout $U/$l 2>/dev/null; cp $p $LA/ && launchctl bootstrap $U $LA/${p:t} && echo "installed $l"
  fi
done
for p in $LA/com.nick.miniheroes-*.plist(N); do
  [[ -f $REPO/schedules/${p:t} ]] || { launchctl bootout $U/${p:t:r} 2>/dev/null; rm $p; echo "removed ${p:t:r}"; }
done
echo "--- schedules"
for p in $LA/com.nick.miniheroes-*.plist(N); do
  l=${p:t:r}
  t=$(plutil -extract StartCalendarInterval json -o - $p 2>/dev/null)
  st=$(launchctl print $U/$l 2>/dev/null | awk -F' = ' '/last exit code/{print $2; exit}')
  printf "%-32s %s  last exit: %s\n" $l "$t" "${st:-never run}"
done
