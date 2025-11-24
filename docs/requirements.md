# Goal

Build the web site to demo the election guard

## Design

The backend using python FastAPI , build with uv, to support the web app API for demo the election.
This bakckend will install the lib <https://github.com/Election-Tech-Initiative/electionguard> to implement the service off election. The detail document of this lib is that the REF section at the end of document

The backend support some API

### API  

#### API POST /app/v1/vote-events

request is provide the event name, from and end date, and list of candidate names (ensure unique)

response the event id, name, from, to, status, allow_vote_candidate_num and the list candidate with name & id

the event can have some event like INIT, INVOTING, TALLING,  END

related to the demo scope, it should create with INVOTING state

#### API POST /app/v1/gen-customer-fake-token

Get input the unique id string, example the people name and then unique token as customer secret, for an example uuid

#### API POST /app/v1/customer-vote

will send the request with customer-secret and list of chosen candidate with {id, name}, and vote_event_id

the API will
(1) verify as identify right customer by customer-secret
(2) ensure the right allow candidate and on valid event duration (from, to) and the event status is INVOTING, and check sufficient candiate must to vote based on event setting
(3) idempotency to ensure one customer can vote maximum one times on an event
(4) using correct to work on the service use the right functions on election-guard with design business for this step ~ like encrypt or safe store the vote, just double check the right election business here on this SDK
(5) return the election-vote-secret

#### API POST /app/v1/verify-customer-vote/:vote-secret

will send the to API the vote secret, the API will return
{ event_id, event_name, event_status, from, to, customer name, vote candidates (list candidate name & id), vote_event (name, id, from, to), vote_at}

Ensure which client

#### API POST /app/v1/execute-tally-election/:event_id

trigger the full process off tally-election, the status should update to TALLING
this API will use election-guard to process correct way respect this document workflow
after finish, the event should update to END
return the payload as

```
{
  event: {
    name, id, status, from, to, end_at,
    allow_vote_candidate_num,
    candidates: [{name, election-guard--how-vote-work}]
    status,
    total_votes,
    vote_statistic: [
       candidate_name,
       candidate_id,
       vote_num,
       percent_vote,
    ],
    winner: {
      candidate_name,
      candidate_id,
      vote_num,
      percent_vote
    }
  }
}
```

#### API GET /app/v1/vote_events/:event_id

return the same output of POST/tally-election

### Backend log  

IMPORTANT:  MUST provide the detail log on backend on each step to proven safe election-guard

## Database design

Can use the sqlite to this MVP demo

## Single website for testing

Create the single html site for testing the API demo the votes process
ALlow to use the shard UI with CDN

The layout of frontend
(1) Session create event
input from with event name, from, to and list of candidate name
then can create the voting event

(2) Session customer vote  (left column)
From the created event on the top/event session
on the left side (column left)

The are 3 section on this
(2.1) Create customer, by input the name, will call the api /app/v1/gen-customer-fake-token
and there is table customes will add new customer record (name, custome-secrect)
(2.2) the vote form:
by select the customer
select list of candidate have to vote from dropdown, this candidate get from the created event before
then an button vote to call correct API /app/v1/customer-vote

Then the result will add the the table customer votes
The record of this table should have the button `Verify`, when click on this will show the vote detail by calling the API /app/v1/verify-customer-vote

(3) session Votes Result (right column)
Create the button TALLY_ELECTION to trigger correct API  POST /app/v1/execute-tally-election/:event_id
the result should be two section:
3.1 winner
3.2 the table statistic sort by vote num desc

we also support the refresh button to update the winner session and table by calling the get /app/v1/vote-events/:event_id

## REF

Document for the SDK election-guard lib:

- docs/election-guarl--business-terms.md
- docs/election-guard--how-vote-work.md

Document for fastAPI best practice

- docs/fast-api-best-practices.md
