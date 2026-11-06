"""Create an AI-authored diagnostic corpus and genuinely blank human rating sheets.

Design labels are drafting metadata, NEVER human gold labels. Do not tune VADER
against these items. Human reference evaluation is enabled only after real ratings.
"""
from pathlib import Path
import csv
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parents[1]
SEED = 8240
# domain, intended base tone, base, negation, modifier, contrast
FAMILIES = [
('apps','positive','The calendar app is useful.','The calendar app is not useful.','The calendar app is very useful.','The calendar app is useful, but its reminders are annoying.'),
('apps','positive','The photo editor is excellent.','The photo editor is not excellent.','The photo editor is really excellent.','The photo editor is excellent, but exporting pictures is frustrating.'),
('apps','positive','The navigation app is helpful.','The navigation app is not helpful.','The navigation app is extremely helpful.','The navigation app is helpful, but its location tracking is awful.'),
('apps','positive','The reading app is enjoyable.','The reading app is not enjoyable.','The reading app is very enjoyable.','The reading app is enjoyable, but the subscription is terrible.'),
('apps','negative','The budgeting app is confusing.','The budgeting app is not confusing.','The budgeting app is very confusing.','The budgeting app is confusing, but the support team is excellent.'),
('apps','negative','The fitness app is disappointing.','The fitness app is not disappointing.','The fitness app is really disappointing.','The fitness app is disappointing, but its exercise videos are helpful.'),
('apps','negative','The shopping app is frustrating.','The shopping app is not frustrating.','The shopping app is extremely frustrating.','The shopping app is frustrating, but the refunds are reliable.'),
('apps','negative','The music app is awful.','The music app is not awful.','The music app is very awful.','The music app is awful, but its song recommendations are great.'),
('apps','neutral','The notes app has a settings page.','The notes app does not have a settings page.','The notes app has exactly one settings page.','The notes app has a settings page, but finding saved notes is frustrating.'),
('apps','neutral','The weather app lists three cities.','The weather app does not list three cities.','The weather app lists exactly three cities.','The weather app lists three cities, but its forecasts are excellent.'),
('apps','neutral','The messaging app uses a blue icon.','The messaging app does not use a blue icon.','The messaging app uses a completely blue icon.','The messaging app uses a blue icon, but sending attachments is terrible.'),
('apps','neutral','The timer app displays the date.','The timer app does not display the date.','The timer app displays the full date.','The timer app displays the date, but its simple controls are helpful.'),
('transport','positive','The train service is reliable.','The train service is not reliable.','The train service is very reliable.','The train service is reliable, but the station announcements are confusing.'),
('transport','positive','The bus driver is friendly.','The bus driver is not friendly.','The bus driver is very friendly.','The bus driver is friendly, but the late departures are annoying.'),
('transport','positive','The bicycle rental is convenient.','The bicycle rental is not convenient.','The bicycle rental is really convenient.','The bicycle rental is convenient, but the broken locks are frustrating.'),
('transport','positive','The taxi ride is comfortable.','The taxi ride is not comfortable.','The taxi ride is extremely comfortable.','The taxi ride is comfortable, but the unexpected fee is unfair.'),
('transport','negative','The ferry service is disappointing.','The ferry service is not disappointing.','The ferry service is very disappointing.','The ferry service is disappointing, but the crew is friendly.'),
('transport','negative','The ticket machine is frustrating.','The ticket machine is not frustrating.','The ticket machine is really frustrating.','The ticket machine is frustrating, but the staff are helpful.'),
('transport','negative','The airport transfer is terrible.','The airport transfer is not terrible.','The airport transfer is very terrible.','The airport transfer is terrible, but the driver is excellent.'),
('transport','negative','The tram connection is confusing.','The tram connection is not confusing.','The tram connection is extremely confusing.','The tram connection is confusing, but the journey planner is useful.'),
('transport','neutral','The bus departs at nine.','The bus does not depart at nine.','The bus departs at exactly nine.','The bus departs at nine, but the long wait is annoying.'),
('transport','neutral','The train has six carriages.','The train does not have six carriages.','The train has exactly six carriages.','The train has six carriages, but the spacious seats are comfortable.'),
('transport','neutral','The ferry stops at two terminals.','The ferry does not stop at two terminals.','The ferry stops at exactly two terminals.','The ferry stops at two terminals, but the boarding process is awful.'),
('transport','neutral','The station has an east entrance.','The station does not have an east entrance.','The station has a separate east entrance.','The station has an east entrance, but the clear signs are helpful.'),
('university','positive','The library desk is helpful.','The library desk is not helpful.','The library desk is very helpful.','The library desk is helpful, but the booking website is terrible.'),
('university','positive','The tutor is supportive.','The tutor is not supportive.','The tutor is extremely supportive.','The tutor is supportive, but the assessment instructions are confusing.'),
('university','positive','The laboratory session is enjoyable.','The laboratory session is not enjoyable.','The laboratory session is very enjoyable.','The laboratory session is enjoyable, but the equipment is unreliable.'),
('university','positive','The enrolment adviser is friendly.','The enrolment adviser is not friendly.','The enrolment adviser is really friendly.','The enrolment adviser is friendly, but the delayed response is frustrating.'),
('university','negative','The timetable portal is confusing.','The timetable portal is not confusing.','The timetable portal is very confusing.','The timetable portal is confusing, but the printed guide is useful.'),
('university','negative','The campus shuttle is disappointing.','The campus shuttle is not disappointing.','The campus shuttle is really disappointing.','The campus shuttle is disappointing, but the driver is friendly.'),
('university','negative','The accommodation office is unhelpful.','The accommodation office is not unhelpful.','The accommodation office is extremely unhelpful.','The accommodation office is unhelpful, but the maintenance team is excellent.'),
('university','negative','The online lecture is boring.','The online lecture is not boring.','The online lecture is very boring.','The online lecture is boring, but the discussion afterwards is enjoyable.'),
('university','neutral','The library opens at eight.','The library does not open at eight.','The library opens at exactly eight.','The library opens at eight, but the study rooms are excellent.'),
('university','neutral','The seminar takes place in room twelve.','The seminar does not take place in room twelve.','The seminar takes place in exactly the same room.','The seminar takes place in room twelve, but the noise outside is annoying.'),
('university','neutral','The course has two tutorials.','The course does not have two tutorials.','The course has exactly two tutorials.','The course has two tutorials, but the practical examples are helpful.'),
('university','neutral','The student card contains a photograph.','The student card does not contain a photograph.','The student card contains one additional photograph.','The student card contains a photograph, but replacing it is frustrating.'),
('service','positive','The booking agent is helpful.','The booking agent is not helpful.','The booking agent is very helpful.','The booking agent is helpful, but the refund process is frustrating.'),
('service','positive','The repair service is excellent.','The repair service is not excellent.','The repair service is really excellent.','The repair service is excellent, but the appointment system is awful.'),
('service','positive','The delivery team is reliable.','The delivery team is not reliable.','The delivery team is very reliable.','The delivery team is reliable, but the damaged packaging is disappointing.'),
('service','positive','The receptionist is friendly.','The receptionist is not friendly.','The receptionist is extremely friendly.','The receptionist is friendly, but the hidden charge is unfair.'),
('service','negative','The refund process is frustrating.','The refund process is not frustrating.','The refund process is very frustrating.','The refund process is frustrating, but the adviser is helpful.'),
('service','negative','The support chat is useless.','The support chat is not useless.','The support chat is really useless.','The support chat is useless, but the telephone team is excellent.'),
('service','negative','The cancellation policy is unfair.','The cancellation policy is not unfair.','The cancellation policy is extremely unfair.','The cancellation policy is unfair, but the agent is supportive.'),
('service','negative','The waiting area is unpleasant.','The waiting area is not unpleasant.','The waiting area is very unpleasant.','The waiting area is unpleasant, but the staff are friendly.'),
('service','neutral','The receipt lists two items.','The receipt does not list two items.','The receipt lists exactly two items.','The receipt lists two items, but the unexpected charge is unfair.'),
('service','neutral','The help desk closes at five.','The help desk does not close at five.','The help desk closes at exactly five.','The help desk closes at five, but the email response is helpful.'),
('service','neutral','The parcel has a tracking number.','The parcel does not have a tracking number.','The parcel has a separate tracking number.','The parcel has a tracking number, but the delivery delay is frustrating.'),
('service','neutral','The appointment is on Thursday.','The appointment is not on Thursday.','The appointment is on this coming Thursday.','The appointment is on Thursday, but the early confirmation is reassuring.'),
]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def build():
    for existing in (ROOT/'annotations').glob('annotator_*.csv'):
        with existing.open(newline='',encoding='utf-8') as f:
            if any(row.get('sentiment','').strip() for row in csv.DictReader(f)):
                raise RuntimeError(f'Refusing to overwrite real rating work: {existing.name}')
    assert len(FAMILIES)==48
    # One family of each base tone in each domain is development-only.
    # No scores or labels were inspected to choose this deterministic split.
    dev={0,4,8,12,16,20,24,28,32,36,40,44}
    rows=[]
    for i,(domain,tone,base,negation,modifier,contrast) in enumerate(FAMILIES):
        word=base.rstrip('.').split()[-1]
        caps=base[:base.rfind(word)] + word.upper() + '.'
        variants=[base,negation,modifier,caps,base.rstrip('.')+'!!!',contrast]
        for condition,text in zip(['base','negation','modifier','capitals','punctuation','contrast'],variants):
            identity=hashlib.sha256(f'8240:{i}:{condition}'.encode()).hexdigest()[:10]
            rows.append(dict(item_id='C'+identity,family_id=f'F{i+1:02}',domain=domain,
                condition=condition,split='development' if i in dev else 'test',
                design_base_tone=tone,text=text,provenance='AI-assisted authored diagnostic; no human gold labels'))
    assert len({r['text'] for r in rows})==288
    write_csv(ROOT/'data/constructed.csv',rows,list(rows[0]))
    for annotator,seed in [('A',8241),('B',8242)]:
        ordered=rows.copy();random.Random(seed).shuffle(ordered)
        blank=[dict(item_id=r['item_id'],text=r['text'],sentiment='',intensity='',confidence='',notes='') for r in ordered]
        write_csv(ROOT/f'annotations/annotator_{annotator}.csv',blank,list(blank[0]))
    # One complete six-item family per domain/tone cell; 10 held-out families.
    test_families=sorted({r['family_id'] for r in rows if r['split']=='test'})
    sample_families=random.Random(SEED).sample(test_families,10)
    judge=[{'item_id':r['item_id'],'text':r['text']} for r in rows if r['family_id'] in sample_families]
    random.Random(SEED+3).shuffle(judge)
    (ROOT/'annotations/llm_constructed_input.json').write_text(json.dumps(judge,indent=2)+'\n')
    (ROOT/'data/constructed_manifest.json').write_text(json.dumps({
       'seed':SEED,'families':48,'items':288,'domains':4,'conditions':6,
       'development_families':12,'development_items':72,'test_families':36,'test_items':216,
       'authorship':'Drafted by the ChatGPT/Codex assistant on 2026-11-04; reviewed for obvious grammar and duplicate strings.',
       'human_annotation_completed':False,'design_tones_are_gold':False,
       'split_policy':'One preselected positive, negative and neutral family per domain held for development.',
       'llm_sample_families':sample_families},indent=2)+'\n')
    print('Created 288 diagnostic texts and two blank human rating sheets.')

if __name__=='__main__': build()
