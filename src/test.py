import sporty.users as u
import glob

uids = [111397971,
        1115884644,
        111636637,
        1118674309,
        1120500210,
        112091139,
        112203950,
        1122204780]
users = u.api(uids)
users.getMostSimilarFriend('../inputs/users/', '../inputs/friends/')
