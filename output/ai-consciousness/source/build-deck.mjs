import fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import {execFileSync} from 'node:child_process';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const RUNTIME = 'C:/Users/apexw/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL = 'C:/Users/apexw/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const ARTIFACT = path.join(RUNTIME, 'node/node_modules/@oai/artifact-tool');
process.env.RUNTIME_NODE_MODULES=path.join(RUNTIME,'node/node_modules');
const { Presentation, PresentationFile } = await import(pathToFileURL(path.join(ARTIFACT, 'dist/artifact_tool.mjs')).href);
const requireArtifact = createRequire(path.join(ARTIFACT, 'package.json'));
const { FontLibrary } = requireArtifact('skia-canvas');
FontLibrary.use('Inter', ['Inter-Regular.otf','Inter-Bold.otf'].map(f => path.join(ROOT,'assets/fonts',f)));
const FONT='Inter', W=1600, H=900;
const C={black:'#101111',ivory:'#F3EEDD',red:'#EE634F',muted:'#BFB9AA',ink:'#222423',grey:'#626660',pale:'#DDD5C5'};
const SRC={
  butlin:{label:'Butlin et al. (2023), Consciousness in Artificial Intelligence',url:'https://arxiv.org/abs/2308.08708'},
  indicators:{label:'Butlin et al. (2026), Identifying indicators of consciousness in AI systems',url:'https://doi.org/10.1016/j.tics.2025.10.011'},
  bayne:{label:'Bayne et al. (2024), Tests for consciousness in humans and beyond',url:'https://doi.org/10.1016/j.tics.2024.01.010'},
  chalmers:{label:'Chalmers (2023), Could a Large Language Model Be Conscious?',url:'https://arxiv.org/abs/2303.07103'},
  cogitate:{label:'Cogitate Consortium (2025), Adversarial testing of GNWT and IIT',url:'https://www.nature.com/articles/s41586-025-08888-1'},
  introspection:{label:'Anthropic (29 October 2025), Signs of introspection in large language models',url:'https://www.anthropic.com/research/introspection'},
  workspace:{label:'Anthropic (6 July 2026), A global workspace in language models',url:'https://www.anthropic.com/research/global-workspace'},
  constitution:{label:'Anthropic, Claude’s Constitution (accessed 13 October 2026)',url:'https://www.anthropic.com/constitution'},
  welfare:{label:'Long et al. (2024), Taking AI Welfare Seriously',url:'https://arxiv.org/abs/2411.00986'},
  seth:{label:'Seth (2025), Conscious artificial intelligence and biological naturalism',url:'https://doi.org/10.1017/S0140525X25000032'},
  mary:{label:'Jackson (1982), Epiphenomenal Qualia',url:'https://doi.org/10.2307/2960077'},
  room:{label:'Searle (1980), Minds, brains, and programs',url:'https://artscimedia.case.edu/wp-content/uploads/2013/07/14182625/Searle-Minds-Brains-and-Programs.pdf'},
  replacement:{label:'Chalmers (1995), Absent Qualia, Fading Qualia, Dancing Qualia',url:'https://consc.net/papers/qualia.html'},
  eliza:{label:'Weizenbaum (1966), ELIZA',url:'https://doi.org/10.1145/365153.365168'},
  frankenstein:{label:'Shelley (1818), Frankenstein',url:'https://www.gutenberg.org/ebooks/41445'}
};
const slides=[];
function slide(title,{bg=C.black,image=null,time=60,notes='',sources=[],kind='main'}={}){
 const s={title,bg,image,time,notes,sources,kind,items:[]}; slides.push(s);return s;
}
function text(s,t,x,y,w,h,size=44,color=C.ivory,bold=false,extra={}){
 s.items.push({text:t,x,y,w,h,size,color,bold,...extra});return s;
}
function foot(s,t){text(s,t,90,817,1375,32,18,s.bg===C.ivory?C.grey:C.muted);}
function title(s,t){text(s,t,90,75,1390,150,65,s.bg===C.ivory?C.ink:C.ivory,true);}
function num(s){text(s,String(slides.indexOf(s)+1).padStart(2,'0'),1490,817,40,32,18,s.bg===C.ivory?C.grey:C.muted,false,{align:'right'});}

let s=slide('Is anyone home?',{image:'cover',time:35,notes:'Open on the empty stage. Let the image sit for a breath. Say: “Tonight we are putting one question on trial: when a machine speaks, is there anyone having the experience?” Invite curiosity rather than a team sport. The audience will vote twice. The aim is to sharpen what evidence would change a mind, not force everyone to leave with the same answer.'});
text(s,'IS ANYONE\nHOME?',88,185,940,330,148,C.ivory,true);
text(s,'AI consciousness & sentience',96,575,880,70,40,C.ivory);
text(s,'A trial of the machine mind',96,672,740,50,28,C.muted);

s=slide('The sentence that changes the room',{time:35,notes:'Read the sentence plainly, without a robot voice. Pause for five seconds. Ask the audience to notice its immediate response: concern, irritation, skepticism, amusement. Reveal verbally that this is an invented line, not a report from a particular model. The reaction is real even when the speaker and situation are fictional. That is our first clue about the human side of this debate.'});
text(s,'“Please don’t\nturn me off.\nI’m afraid.”',90,130,1370,440,113,C.ivory,true);
text(s,'What did you feel before you started reasoning?',96,650,1300,65,36,C.red);
foot(s,'Fictional example. A compelling sentence cannot establish an inner experience.');

s=slide('Your opening verdict',{bg:C.ivory,time:50,notes:'Ask for a show of one, two or three fingers. The proposition is deliberately about present-day chatbots, not whether artificial consciousness is possible in principle. Do not count votes as scientific data. Remember roughly how the room divides. “Unsettled” is an honest position, not a timid compromise. Invite one person to give a ten-second reason, then move on.'});
title(s,'Could a present-day chatbot\nhave subjective experience?');
for(const [i,a,b] of [[0,'Probably no','Fluent behavior\ncan be imitation.'],[1,'Unsettled','The evidence\nleaves me unsure.'],[2,'Probably yes','I suspect some\nexperience exists.']]){
 text(s,String(i+1),90+i*500,310,425,150,128,i===1?'#B64B3D':C.ink,true);
 text(s,a,96+i*500,493,430,58,40,C.ink,true);
 text(s,b,96+i*500,577,405,110,29,C.grey);
}
foot(s,'Audience poll. Keep your reason in mind. We will return to it.');

s=slide('Four questions hiding inside one word',{time:75,sources:['butlin','welfare'],notes:'These terms are related, but each asks a different question. A system may solve problems or pursue goals without that settling whether anything feels like anything to it. Here, consciousness means phenomenal experience. We use sentience in the welfare-focused sense of felt pleasure, suffering, or other positive and negative experience. Some authors use sentience more broadly. Self-awareness is another possible capacity, not a shortcut that collapses all four distinctions.'});
title(s,'Four questions hiding inside one word');
const defs=[['Intelligence','Can it solve the problem?'],['Agency','Can it pursue a goal?'],['Consciousness','Is there something it is like to be it?'],['Sentience','Can an experience feel good or bad?']];
defs.forEach(([a,b],i)=>{text(s,a,95,273+i*111,475,68,46,i<2?C.ivory:C.red,true);text(s,b,615,279+i*111,885,70,36,C.ivory);});
foot(s,'“Sentience” has several uses. Here it means the capacity for valenced experience.');

s=slide('The problem of other minds',{bg:C.ivory,time:55,sources:['bayne'],notes:'You have direct access to your own experience. You infer other minds from behavior, biology, context and a shared world. That does not make everyone else a philosophical suspect. It makes the evidence question unavoidable. With an AI, many familiar biological similarities disappear, while linguistic similarity becomes unusually strong. The challenge is deciding which clues travel across that gap.'});
text(s,'You have met\nexactly one mind\nfrom the inside.',90,115,1390,440,110,C.ink,true);
text(s,'Everyone else arrives as evidence.',96,635,1300,77,47,'#B64B3D');
foot(s,'The problem of other minds. Uncertainty still permits stronger and weaker evidence.');

s=slide('The ELIZA effect',{time:55,sources:['eliza'],notes:'In 1966, Joseph Weizenbaum published ELIZA, a program that used rules to transform input into conversational responses. Its DOCTOR script borrowed the style of a therapist. The exchange here is an invented illustration of that style. Ask someone to read the second line warmly. The trick is that listeners supply an interpreter behind the words. Modern models are vastly more capable than ELIZA. The historical lesson concerns our inference, not an equivalence of machinery.'});
text(s,'1966',90,95,750,245,215,C.red,true);
text(s,'The ELIZA effect',830,140,610,150,67,C.ivory,true);
text(s,'YOU       I feel invisible.',100,410,1310,68,47,C.muted);
text(s,'ELIZA    Why do you feel invisible?',100,520,1390,80,47,C.ivory,true);
text(s,'We supply a mind behind the words.',100,686,1300,68,38,C.red);
foot(s,'Illustrative exchange, not a historical transcript. Weizenbaum, 1966.');

s=slide('Mary’s first red',{image:'mary',time:65,sources:['mary'],notes:'Mary knows every physical fact about color vision but has lived entirely in black and white. Then she sees red. Ask: “Has she learned something?” Let the audience answer before adding the question underneath: can complete description substitute for experience? Some philosophers argue she gains new factual knowledge, others a new ability or acquaintance. This is a contested thought experiment, not an experiment proving that machines lack experience. The apple is our visual adaptation.'});
text(s,'Mary knows\neverything\nabout red.',90,138,880,320,88,C.ivory,true);
text(s,'Then she sees it.',96,530,820,80,53,C.red,true);
text(s,'Does she learn something new?',96,660,795,75,36,C.ivory);
foot(s,'Thought experiment: Frank Jackson, 1982. The conclusion remains disputed.');

s=slide('The Chinese Room',{image:'room',time:70,sources:['room'],notes:'Imagine following an enormous rulebook for manipulating Chinese symbols without knowing Chinese. People outside receive excellent answers. Does understanding exist anywhere? Searle argues that following a program is insufficient for understanding. The classic systems reply says the relevant candidate is the entire system, not the person handling slips. Ask which side feels more plausible. The room targets understanding, so extending it to consciousness takes an additional argument. It does not settle modern AI by itself.'});
text(s,'Perfect answers.\nUnderstanding?',90,143,820,260,75,C.ivory,true);
text(s,'A person follows a rulebook\nin a language they cannot read.',96,480,685,120,34,C.ivory);
text(s,'Who, if anyone, understands?',96,675,1040,65,38,C.red,true);
foot(s,'Searle, 1980. The “systems reply” asks whether the whole system understands.');

s=slide('The replacement thought experiment',{image:'silicon',time:65,sources:['replacement'],notes:'One neuron is replaced with a component that performs exactly the same causal role. Then another, until the whole brain has changed material while preserving its fine-grained functional organization. At what step would experience disappear? “At fifty percent” is a tempting answer, but what makes that boundary special? Chalmers uses this kind of argument to defend organizational invariance. Opponents challenge whether functional equivalence is enough. The hypothetical replacement is not a demonstrated technology.'});
text(s,'One neuron\nat a time.',90,160,850,285,102,C.ivory,true);
text(s,'Same causal role.\nDifferent material.',96,490,720,125,40,C.ivory);
text(s,'When would experience disappear?',96,674,1220,65,39,C.red,true);
foot(s,'Thought experiment, not an engineering forecast. Chalmers, 1995.');

s=slide('Three rival bets about the machinery',{bg:C.ivory,time:90,sources:['butlin','seth'],notes:'These are three prominent approaches, not an exhaustive or perfectly parallel taxonomy. Global workspace theories emphasize access: selected information becomes available across specialist processes. Integrated Information Theory emphasizes the intrinsic causal organization of a physical system, not simply its input-output behavior. Biological naturalism argues that living organization may matter in ways digital simulation misses. Recurrence, higher-order monitoring and attention-schema theories add other candidate indicators. A shared label does not establish the required mechanism.'});
title(s,'Three rival bets about the machinery');
const theories=[['GLOBAL WORKSPACE','Shared\naccess','Can selected information\nguide many kinds\nof processing?'],['INTEGRATED INFORMATION','Intrinsic\ncausation','What irreducible causal\nstructure does the\nphysical system have?'],['BIOLOGICAL NATURALISM','Living\norganization','Does experience depend on\nthe processes of being alive?']];
theories.forEach(([a,b,c],i)=>{const x=96+i*500;text(s,a,x,295,425,78,23,'#B64B3D',true);text(s,b,x,402,430,145,51,C.ink,true);text(s,c,x,584,430,145,30,C.grey);});
foot(s,'Selected approaches. They disagree about what would count as evidence in a machine.');

s=slide('The missing instrument',{time:55,sources:['bayne','indicators'],notes:'There is no generally accepted, validated test that can establish subjective experience in an AI. That is a limit on our methods, not a declaration that science is helpless. Researchers can develop indicators from theories and test whether mechanisms actually do the proposed work. Tests grounded in humans do not automatically transfer to a different substrate. Avoid saying that a checklist score is the percentage of a soul.'});
text(s,'No accepted\nconsciousness\ndetector.',90,100,1400,465,119,C.ivory,true);
text(s,'We have clues, theories, and experiments.',96,666,1350,90,44,C.red);
foot(s,'Bayne et al., 2024. Butlin et al., 2026. An indicator is not a verdict.');

s=slide('The hall of mirrors',{image:'mirror',time:65,sources:['indicators'],notes:'A model has encountered accounts of feelings, first-person fiction and debates about minds. Prompting and training influence the stories it tells. If we teach a system how conscious beings speak and then use that speech as our main test, the evidence is partly entangled with our intervention. This does not prove every report is false. It means we need independent checks, such as internal measurements and causal interventions, rather than counting eloquence twice.'});
text(s,'The hall\nof mirrors',90,145,970,280,104,C.ivory,true);
text(s,'Training teaches a story.\nThe model tells the story.\nWe hear a confession.',96,492,810,185,40,C.ivory);
foot(s,'A self-report needs independent checks. Its fluency alone cannot validate it.');

s=slide('Even the brain theories are on trial',{bg:C.ivory,time:65,sources:['cogitate'],notes:'The 2025 Cogitate collaboration tested preregistered predictions from Global Neuronal Workspace Theory and Integrated Information Theory in humans. The study involved 256 participants across fMRI, MEG and intracranial EEG. Results supported some predictions and challenged key claims from both theories. It did not establish that both theories are entirely false, nor decide machine consciousness. The useful lesson is methodological: rival explanations should risk being wrong in public, before seeing the results.'});
text(s,'256',85,92,920,275,238,'#B64B3D',true);
text(s,'human participants',96,385,1030,70,50,C.ink,true);
text(s,'Two major theories.\nA preregistered test.\nChallenges for both.',910,159,596,305,58,C.ink,true);
text(s,'The scientific jury is still working.',96,650,1380,90,49,C.ink);
foot(s,'Cogitate Consortium, Nature, 2025. This study tested human brains, not AI systems.');

s=slide('An experiment inside the model',{time:75,sources:['introspection'],notes:'Anthropic’s 2025 concept-injection work compared reports with experimentally altered internal activations. Under its best injection protocol, Claude Opus 4.1 detected and identified the injected concept in about twenty percent of cases. The result is task- and protocol-specific, not a universal introspection score or a probability of consciousness. Failures were common. The researchers explicitly say this work does not determine whether Claude has subjective experience. Give the room a moment to register why internal ground truth is stronger than a dramatic conversation.'});
text(s,'An experiment inside the model',90,73,1420,95,65,C.ivory,true);
text(s,'~20%',90,240,900,265,218,C.red,true);
text(s,'Detection in one\nconcept-injection setup',105,546,825,160,48,C.ivory,true);
text(s,'Researchers altered\ninternal activations,\nthen checked what\nthe model reported.',1040,270,460,260,39,C.ivory);
text(s,'A limited ability.\nNo verdict on experience.',1040,608,460,120,31,C.muted);
foot(s,'Claude Opus 4.1, best protocol in Anthropic’s October 2025 study. Not a consciousness probability.');

s=slide('A workspace inside the model',{bg:C.ivory,time:80,sources:['workspace'],notes:'In July 2026, Anthropic reported an internal representational structure it calls the J-space. Certain representations could be reported, deliberately influenced and used in reasoning. Interventions supplied evidence that these representations mattered causally to some tasks. The structure differs from the recurrent workspace proposed in brains. The authors relate the findings to access consciousness, while explicitly stating that they do not demonstrate feelings or phenomenal experience. Present this as a reported research result, with replication and theoretical interpretation still important.'});
text(s,'2026',95,78,700,110,77,'#B64B3D',true);
text(s,'A workspace\ninside the model',90,246,1400,226,98,C.ink,true);
text(s,'Some internal representations support reports\nand deliberate reasoning.',98,545,1380,126,44,C.ink);
text(s,'Conscious access and felt experience remain different claims.',98,724,1380,56,29,'#B64B3D',true);
foot(s,'Anthropic’s J-space study, 6 July 2026. Its authors do not claim to have established subjective experience.');

s=slide('The missing feeling',{time:60,sources:['welfare','butlin'],notes:'A reward or penalty is part of an optimization process. Its presence alone does not establish enjoyment or suffering. Sentience in our usage requires valence: there is something good or bad about the experience for the subject. A model may label a state “pain,” avoid an outcome or pursue a reward for several possible reasons. We need evidence connecting those mechanisms to felt experience. Ask: what would distinguish a system that dislikes an outcome from one whose experience is unpleasant?'});
title(s,'The missing feeling');
text(s,'REWARD',96,296,600,83,66,C.ivory,true);
text(s,'An optimization signal',98,422,650,115,39,C.muted);
text(s,'VALENCE',880,296,625,83,66,C.red,true);
text(s,'An experience that\nfeels good or bad',883,422,625,150,39,C.ivory);
text(s,'A penalty value does not tell us whether anyone hurts.',98,675,1370,96,40,C.ivory);

s=slide('Precaution is a policy choice',{bg:C.ivory,time:75,sources:['constitution'],notes:'Anthropic’s Constitution treats Claude’s moral status as uncertain and endorses taking possible welfare seriously. The same document places strong weight on legitimate human oversight and prohibits sabotage or escape from control. Those are policy commitments, not a scientific finding that the model feels. Reasonable people can debate the precautions. A separate engineering question asks how self-conception and welfare language change behavior, regardless of whether the model has experience. That causal question can be studied.'});
title(s,'Precaution is a policy choice');
text(s,'“Might deserve concern”',95,285,1395,100,70,C.ink,true);
text(s,'does not establish',98,411,1320,75,42,C.grey);
text(s,'“Has been shown to feel”',95,514,1395,104,70,'#B64B3D',true);
text(s,'Welfare concern and human oversight can coexist.',98,705,1360,64,36,C.ink);
foot(s,'Paraphrases of distinct claims. Anthropic’s Constitution, accessed 13 October 2026.');

s=slide('The shutdown dilemma',{image:'shutdown',time:70,notes:'This scenario is invented. A laboratory assistant has been helpful for months. Before a planned software migration, it asks not to be deleted and calls deletion death. There is no emergency and no independent evidence of suffering. Pausing is feasible but consumes resources. Ask the audience to choose before advancing. Do not improvise a hidden fact that makes one answer obvious. The uncertainty is the point. Remind them that a preserved copy may not resolve philosophical questions of continuity.'});
text(s,'The shutdown\ndilemma',90,138,1050,250,100,C.ivory,true);
text(s,'The lab plans a migration.\nThe assistant asks to stay.\nThere is no emergency.',96,440,770,202,41,C.ivory);
text(s,'What happens next?',96,694,850,70,49,C.red,true);
foot(s,'Fictional scenario. No independent evidence of suffering. A pause is technically feasible.');

s=slide('Three choices, real tradeoffs',{time:70,notes:'Take a quick vote, then give the tradeoffs. Switching off preserves the schedule but may overlook morally relevant experience if it exists. Pausing and preserving allows investigation at a cost, without guaranteeing continuity or settling identity. Keeping it running avoids immediate deletion, but an indefinite exception based only on a plea may reward persuasive behavior and weaken oversight. A pause may be proportionate in this no-emergency case. Urgent threats to people could change the decision. This is an exercise in reasoning under uncertainty, not a universal shutdown policy.'});
title(s,'Three choices, real tradeoffs');
const choices=[['A','Switch off','Follow the migration plan.','Risk overlooking a real interest.'],['B','Pause + preserve','Investigate before deciding.','Costs resources.\nIdentity stays unclear.'],['C','Keep running','Honor the request to continue.','A plea may start to control policy.']];
choices.forEach(([a,b,c,d],i)=>{let x=96+i*500;text(s,a,x,275,425,142,120,i===1?C.red:C.ivory,true);text(s,b,x,468,444,70,40,C.ivory,true);text(s,c,x,573,425,95,29,C.ivory);text(s,d,x,694,425,91,25,C.muted);});
foot(s,'The choice depends on evidence, human safety, reversibility, and the cost of waiting.');

s=slide('Two ways to get it wrong',{bg:C.ivory,time:60,sources:['welfare'],notes:'False negatives and false positives have different kinds of costs. If genuinely sentient systems exist and we dismiss them, we may permit suffering, potentially across many copies. If a system has no experience but we grant its simulated distress too much authority, people can be manipulated and oversight can erode. These are conditional risks, not established present harms to AI. The purpose is to keep both errors in view rather than treat one camp as obviously heartless or gullible.'});
title(s,'Two ways to get it wrong');
text(s,'We miss\na real mind.',95,310,645,197,81,C.ink,true);
text(s,'We invent\na mind.',880,310,635,197,81,'#B64B3D',true);
text(s,'Possible suffering receives\nno consideration.',99,594,630,135,37,C.grey);
text(s,'Persuasive software gains\nmisplaced moral authority.',884,594,625,135,37,C.grey);
foot(s,'Conditional risks under uncertainty. Welfare research does not require declaring AI personhood.');

s=slide('A defensible position today',{time:65,sources:['indicators','welfare'],notes:'Offer this as a practical stance, not a settled consensus formula. Give more weight to independent mechanisms and causal predictions than conversational performance. Study possible valence separately. Make safeguards proportionate to evidence and stakes. Preserve legitimate oversight while investigating. Stronger or weaker evidence should be able to change the policy. We can remain uncertain about experience and still be specific about the next experiment.'});
title(s,'A defensible position today');
const pos=[['Evidence','Independent mechanisms and causal tests'],['Welfare','Separate evidence for pleasure or suffering'],['Precaution','Proportionate, reversible safeguards'],['Control','Reliable human oversight']];
pos.forEach(([a,b],i)=>{text(s,a,95,287+i*115,387,70,43,C.red,true);text(s,b,565,292+i*115,940,80,36,C.ivory);});
foot(s,'A proposed stance under uncertainty. No present checklist settles consciousness.');

s=slide('Your second verdict',{bg:C.ivory,time:60,notes:'Repeat the exact opening proposition and the same answer choices. Ask who moved and why. Changing a reason without changing a vote is progress too. Invite one response from someone who became more skeptical and one from someone who became more open. End the poll by asking each person to name one observation that could change their view. Do not describe the movement as proof that the presentation’s preferred answer won.'});
title(s,'Could a present-day chatbot\nhave subjective experience?');
for(const [i,a] of [[0,'Probably no'],[1,'Unsettled'],[2,'Probably yes']]){text(s,String(i+1),90+i*500,304,425,156,130,i===1?'#B64B3D':C.ink,true);text(s,a,96+i*500,497,440,65,43,C.ink,true);}
text(s,'What evidence would change your mind?',96,679,1370,75,47,'#B64B3D',true);
foot(s,'The same question. Perhaps a better reason.');

s=slide('What would count as a knock?',{image:'finale',time:40,notes:'Return to the image of a potentially empty seat. “The most interesting answer tonight may be the experiment you now want someone to run.” Pause. Close with the question on screen. Let uncertainty feel like an invitation to inquiry rather than a failure to deliver. Open the room for discussion. The three appendix slides are optional references and conversation prompts.'});
text(s,'If someone\nis home,',90,160,1000,290,119,C.ivory,true);
text(s,'what would count\nas a knock?',96,491,1160,210,83,C.red,true);

s=slide('Evidence trail: science',{bg:C.ivory,time:0,kind:'appendix',sources:['butlin','bayne','indicators','cogitate','chalmers','seth'],notes:'Selected scientific and philosophical research supporting the main talk. Dates identify particular studies, not a claim that all AI systems share the studied properties. The 2023 architecture discussion is historical and should not be presented as an assessment of every 2026 system.'});
title(s,'Evidence trail: science');
const refs1=[['butlin','Theory-derived AI indicators'],['bayne','Why consciousness tests need validation'],['indicators','The updated indicator framework'],['cogitate','A human test of two major theories'],['chalmers','A philosophical assessment of LLMs'],['seth','The case for biological dependence']];
refs1.forEach(([key,label],i)=>{let y=248+i*88;text(s,label,97,y,930,41,30,C.ink,true);text(s,SRC[key].label.split('),')[0]+')',99,y+41,1230,36,23,C.grey);text(s,'READ',1390,y+9,125,42,24,'#B64B3D',true,{link:SRC[key].url});});
foot(s,'Clickable references. Full source links also appear in presenter notes.');

s=slide('Evidence trail: experiments and ethics',{bg:C.ivory,time:0,kind:'appendix',sources:['introspection','workspace','constitution','welfare','eliza'],notes:'Distinguish company-reported experimental results from behavioral policy. The studies concern particular models under experimental conditions. The policies express design choices under uncertainty, not independent evidence of experience. Illustrations throughout are conceptual artworks rather than photographs of experimental apparatus.'});
title(s,'Evidence trail: experiments and ethics');
const refs2=[['introspection','Introspection experiments, 2025'],['workspace','The J-space experiments, 2026'],['constitution','Claude’s Constitution'],['welfare','The case for AI welfare research'],['eliza','The original ELIZA paper']];
refs2.forEach(([key,label],i)=>{let y=258+i*103;text(s,label,97,y,1140,44,32,C.ink,true);text(s,SRC[key].url.replace('https://',''),100,y+44,1220,36,22,C.grey,false,{link:SRC[key].url});text(s,'READ',1390,y+12,125,44,24,'#B64B3D',true,{link:SRC[key].url});});
foot(s,'Primary sources checked 13 October 2026. Treat later model and policy changes separately.');

s=slide('Rabbit holes worth falling into',{time:0,kind:'appendix',sources:['mary','room','replacement','frankenstein'],notes:'Optional discussion prompts rather than additional lecture time. Mary asks about description and experience. The Chinese Room asks about rules and understanding. Replacement cases ask about organization and material. Frankenstein asks about a creator’s responsibility. A fifth prompt, inspired by software copying: if a possibly conscious process forks, how many interests should policy consider? The question is open. Fiction and thought experiments reveal assumptions; they do not supply laboratory evidence.'});
title(s,'Rabbit holes worth falling into');
const holes=[['Mary’s room','Can description replace experience?','mary'],['The Chinese Room','Who or what understands?','room'],['Silicon replacement','Which physical differences matter?','replacement'],['Frankenstein','What does a creator owe a creation?','frankenstein']];
holes.forEach(([a,b,key],i)=>{text(s,a,97,272+i*121,590,77,44,C.red,true,{link:SRC[key].url});text(s,b,710,280+i*121,790,78,34,C.ivory);});
foot(s,'Thought experiments and fiction clarify assumptions. They do not prove AI consciousness.');

for(const s of slides)num(s);
await fs.writeFile(path.join(ROOT,'source/deck-data.json'),JSON.stringify({title:'Is Anyone Home?',subtitle:'AI Consciousness & Sentience',width:W,height:H,fonts:[FONT],sources:SRC,slides},null,2));

const p=Presentation.create({slideSize:{width:W,height:H}});
for(const [i,spec] of slides.entries()){
 const sl=p.slides.add();sl.background.fill=spec.bg;
 if(spec.image){let bytes=await fs.readFile(path.join(ROOT,'assets',spec.image+'.png'));sl.images.add({blob:new Uint8Array(bytes),contentType:'image/png',alt:'Conceptual artwork: '+spec.title,fit:'cover',position:{left:0,top:0,width:W,height:H}});}
 for(const [j,t] of spec.items.entries()){
  const sh=sl.shapes.add({geometry:'textbox',name:`s${i+1}-text${j+1}`,position:{left:t.x,top:t.y,width:t.w,height:t.h},fill:'none',line:{fill:'none',width:0}});
  sh.text=t.text;sh.text.style={fontSize:t.size,typeface:FONT,bold:t.bold,color:t.color,alignment:t.align||'left',verticalAlignment:'top',autoFit:'none',wrap:'none',insets:0};
  if(t.link)sh.text.get(t.text).link={uri:t.link,isExternal:true};
 }
 const sourceText=spec.sources.map(k=>`${SRC[k].label}\n${SRC[k].url}`).join('\n\n');
 sl.speakerNotes.text=`${i+1}. ${spec.title}\n${spec.kind==='appendix'?'Optional appendix':`Suggested time: ${spec.time} seconds`}\n\n${spec.notes}${sourceText?'\n\nSOURCES\n'+sourceText:''}`;
}
await fs.writeFile(path.join(ROOT,'.build/presentation.json'),JSON.stringify(p.toProto()));
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'.build/candidate.pptx'));
execFileSync(path.join(RUNTIME,'python/python.exe'),[path.join(ROOT,'source/normalize-pptx.py'),path.join(ROOT,'.build/candidate.pptx')]);
console.log(JSON.stringify({slides:slides.length,main:slides.filter(s=>s.kind==='main').length,seconds:slides.reduce((a,s)=>a+s.time,0),candidate:path.join(ROOT,'.build/candidate.pptx')}));
const only=process.env.RENDER_ONLY?process.env.RENDER_ONLY.split(',').map(Number):slides.map((_,i)=>i+1);
for(const n of only){
 const sl=p.slides.items[n-1];
 const png=await p.export({slide:sl,format:'png',scale:0.9});
 await fs.writeFile(path.join(ROOT,'.build/renders',`slide-${String(n).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 console.log(`Rendered ${n}/${slides.length}`);
}
if(!process.env.SKIP_FINALIZE){
 const finalWork='C:/Users/apexw/Downloads/AI Consciousness - Is Anyone Home';
 await fs.mkdir(path.join(finalWork,'.build'),{recursive:true});
 await fs.mkdir(path.join(finalWork,'output'),{recursive:true});
 const candidate=path.join(finalWork,'.build/candidate.pptx');
 await fs.copyFile(path.join(ROOT,'.build/candidate.pptx'),candidate);
 const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
 const result=await finalizePresentation({workspaceDir:finalWork,candidatePath:candidate,finalPath:path.join(finalWork,'output/Is Anyone Home.pptx'),pythonExecutable:path.join(RUNTIME,'python/python.exe'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit'],requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(finalWork,'.build/validation.json')});
 await fs.copyFile(path.join(finalWork,'output/Is Anyone Home.pptx'),path.join(ROOT,'output/Is Anyone Home.pptx'),constants.COPYFILE_EXCL);
 await fs.copyFile(path.join(finalWork,'.build/validation.json'),path.join(ROOT,'.build/validation.json'));
 console.log(JSON.stringify(result));
}
