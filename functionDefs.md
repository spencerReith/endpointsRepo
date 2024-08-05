**<u>Function Definitions</u>**<br>
for relevant functions called by the front end

**<u>Introduction<\u>**<br>
this doc describes all the functions needed for retrieving, sending & checking data (for banned users, profanity, etc). It is broken up into three sections. One for data retrieval, one to for sending data to the backend, and one for checking data. The document describes which functions you will need for each page on the front end, and where those functions are found.<br><br>

**<u>Retrieval Functions<\u>**<br><br>

**<u>'getterLib.py'</u>**<br>

**<u>Recruiting Page</u>**<br>
**'getDeck'** – to load a deck of 10 applicants to swipe through<br>
params – db, userID<br>
returns – dictionary keyed by userID:dictionary, where each subdictionary is keyed by<br>
    {<br>
        name:()<br>
        classYear:()<br>
        major:()<br>
        minor:()<br>
        skills:()<br>
        interests:()<br>
        tindarIndex:()<br>
    }<br>
<br>

**<u>Résumé</u>**<br>
**'getProfile'** – to load a user's profile. Can be used to load some other applicant's profile, or one's own profile<br>
params – db, userID<br>
returns – dictionary, keyed as follows<br>
    {<br>
        name:()<br>
        email:()
        classYear:()<br>
        major:()<br>
        minor:()<br>
        skills:()<br>
        interests:()<br>
        tindarIndex:()<br>
        endorsements:()<br>
        blurb:()<br>
    }<br>
**notes** – to load a user's own profile, you will also need to show them how many endorsements and referrals they have remaining. You can use 'getEndRefs' for this information.<br>
also, email is only important to use when calling 'getProfile' to get information for the connections page. Otherwise, we do not want it displayed.

**Function for checking skills/interests length**
overCharLimit(type, message):
put in 'skills' for type if you're checking if skills is over the char limit
put in 'interests' for type if you're checking if interests is over the char limit

**'endorsementLib.fetchEndorsements'** – load all of the endorsements a user has recieved<br>
params – userID<br>
returns – a list of tuples keyed by (sender_id:message), where sender_id represents the userID of the person who send the endorsements.<br>
**notes** –  This will be needed to display on the endorsement leaderboard, and on an individuals profile. However, we are not going to show the endorsements while swiping through cards.<br>

**'getEndRefs'** – to retrieve the amount of endorsements and referrals a user has left to make
params – db, userID<br>
returns – a dictionary, keyes as follows:<br>
{<br>
    remainingEndorsements:()<br>
    remainingReferrals:()<br>
}<br>
**notes** – you should only be allowed to input and endorsement or referral if you have > 0 remaining for the item in question. The button should not work if you have zero remaining

**<u>Endorsements Leaderboard</u>**<br>
**'getLeaderboard'** – to load the leaderboard of most highly endorsed applicants<br>
params – db<br>
returns – dictionary, keyed by rank:userID<br>
**notes** –  Once you have the userID's, you can call 'getProfile' to get all the neccessary information to display<br>

**<u>Connections</u>**<br>
**'getConnections'** – returns all of a given user's connections<br>
params – db, userID<br>
returns – a dictionary containing two objects. The first is is a list of swipingMatches. The second is a list, containing a tuple for every referal. The first element in the tuple is the userID of the person who made the referal, and the second element is the userID of the other person being refered.<br>
**notes** – Once you have the userID's, use 'getProfile' to get any other information you might want to display about the applicant in the chatting module<br>

**<u>'cencorshipLib.py'</u>**
**'contains_prof'** – to check if a string of text contains profanity<br>
params - message<br>
returns - bool; true if message contains profanity, otherwise returns false<br>
**notes** – places where you probably want to use this function: skills, interests, wordsList (for madlib format blurb in resume), endorsements, messaging. If you want me to support a list of words being passed in, let me know that will be easy. Also, if you want me to return the problematic word I can do that too.<br><br>

**'is_banned'** – to check if a user is banned from our site<br>
params - email<br>
returns - bool; true if user is banned, false if user is not banned<br>
**notes** – run this before creating a user<br><br>

**<u>Functions for Sending Data<\u>**<br><br>

**<u>'setterLib.py'</u>**

**'createUser'** - sends all the nec. info to create a new user<br>
params - email, classYear, sex, prefSex<br>
returns - userID<br>
**notes** – function automatically parses and inputs name based on email address. also, auto-generates, stores and returns a userID. Pass that userID to 'createResume' when nec.<br>

**'checkEmail'** - check if the user's email is already registered, or is banned from our service<br>
params – email<br>
returns - keywords indicating if the user is already in our db or is banned<br>
**notes** – this should be run prior to running createUser<br>


**'createResume'** – sends all the nec. info to create a user's resume<br>
params - userID, major, minor, skills, interests, blurbEntries<br>
send dictionary with all the nec. information<br>
returns – n/a<br>

**<u>'analyticsLib.py'</u>**<br>

THESE SHOULD BE DONE WHILE CREATING THE PROFILE
def calcTindarIndex(GPA, ricePurityScore):
    returns a tindar index

def addTindarIndexToDB(userID, tindarIndex):
    adds tindar index to DB

if you want to get tindar index, that can be found inside of get_profile


**<u>'referralLib.py'</u>**

**'attemptReferral'** - attempts to create a referral from one applicant, between another two applicants<br>
params – userID of person making referral, userID of first person being referred, userID of second person being referred<br>
returns – various codes depending on sucess/failure of referral, detailing reason for suc./failure<br>
**notes** – You should use getterLib.getEndRefs() beforehand to show the user how many refs. they have left to make. If that equals 0, they should not be able to attempt a referral.<br>

**<u>'endorsementLib.py'</u>**<br>

**'attemptEndorsement'** – attempts to send an endorsement from one applicant to another<br>
params – userID of person making the endorsement, userID of person being endorsed, message<br>
returns – true upon success, false upon failure<br>
**notes** – You should use getterLib.getEndRefs() beforehand to show the user how many endorsements they have left to make. If that equals 0, they should not be able to attempt an endorsement.<br>

**<u>'algLib.py'</u>**
**'addInteractionToDB'** – adds an interaction to the database. To be called once one user swipes on another<br>
params – who is swiping (a_userID), who they are swiping on (b_userID), weight (swiping decision, see notes)<br>
returns – n/a<br>
**notes** – weight=0 means a rejection, weight=1 means an offer<br>

**'renengInDatabase'** – allows one user to reneg on another<br>
params – who is revoking their offer (a_userID), who they are revoking that offer from (b_userID)<br>
returns – n/a<br>

**'blacklist'** – allows one user to blacklist another<br>
params – who is doing the blacklisting (a_userID), who is being blacklisted (b_userID)<br>
returns – n/a<br>
