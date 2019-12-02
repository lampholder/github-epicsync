# github-epicsync
Translates and synchronises all milestones/issues on on GitHub repo into labels on a configurable set of other GitHub repos.

## Why though?
This is in support of our experiments adopting a more user-focused approach to product development.

All user-facing feature development is now expected to be driven by a _user story_, which itself will usually sit within an _epic_ that groups a set of related user stories which are being tackled at the same time and are working towards meeting the same overarching objective.

To provide this structure within GitHub's relatively unstructure environment, we are:

- compiling user stories in a dedicated repo, at https://github.com/vector-im/user-stories/issues
- gathering related stories being tackled at the same time in milestones, at https://github.com/vector-im/user-stories/milestones
    - representing the relative priority of stories by their prioritisation within their associated milestone
- automatically creating `epic:n` and `story:m` labels within target repos (for now this is vector-im/riot-web, but probably soon also vector-im/riot-ios, vector-im/riot-android and vector-im/riotX-android) so that per-platform implementation issues can be linked back to their parent user story.
- visualising epic progress through the use of the [feature dashboard](https://dashboard.lant.uk/#/plan?epic=vector-im/user-stories/milestone/2&repo=matrix-org/matrix-js-sdk&repo=vector-im/riot-web&repo=vector-im/riot-ios&repo=vector-im/riot-android&repo=vector-im/riotX-android)
