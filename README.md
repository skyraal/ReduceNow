### Built in less than a day for fun!
Demo:
https://youtu.be/xmKQ9Jw_2Fw

###Inspiration

What do you think is the most effective incentive to make people behave more sustainably? If you think it’s money, me too! But apparently we’re wrong. Multiple peer-reviewed research has shown that social framings are more effective than financial. For instance a paper by Asensio & Delmas from the Journal of Economic Behavior & Organization showed that wordings that frames energy savings with information disclosures about the environmental and health implications have a longer impact than ones that disclose the financial savings. Multiple other papers also found the same phenomenon. (link) (link)

Additionally a lot of people want to make a change to make their lives more sustainable but struggle to start or even view it as a huge sacrifice. What I realized is different emission reduction methods might be easier on some then others. For instance, one person might find it easy to carry a reusable water bottle but resist lowering the thermostat. If behavioral messaging focuses on a personalized approach—such as encouraging them to bring a water bottle daily while introducing subtle changes to their heating habits—it frames sustainability as a gradual and manageable process rather than an overwhelming sacrifice. Over time, the habit of carrying a reusable bottle can evolve into larger efforts, like investing in energy-efficient appliances or using smart thermostats to regulate heat​. (link) (link)

This approach leverages psychological principles of incrementalism and ease, where simpler, less demanding steps lead to greater sustainable behaviors.

###What it does

This website helps recommend the easiest "first steps" according to each user's preference and use the research recommended framing to highlight the impact. Such as highlighting the health impacts that they saved.

Users will communicate with a Gemini-powered chatbot that is trained to ask questions about your preference and your habits to recommend a way to reduce emissions and pollutions that is the most comfortable for the users. It'll be doing so in five questions or less and focusing on following up and asking about scenarios.

Then we will forward the user to a page where they can view more information about the method. For instance, if it's recycling, they can scan an item they want to recycle, it'll then be analyzed by Hyperbolic's AI Inference to identify the item, then the inference will also return tutorial/ideas!

Finally, they will be shown to the thank you page where it'll highlight the health and environmental impact that you might've saved by doing these small steps.

###How we built it

Hyperbolic AI Inference:

We used the LLAMA vision hyperbolic model to analyze the items that the user wants to recycle
Then we used hyperbolic text generation to return potential recycling ideas
Finally we used the AI inference to also calculate the estimated emissions or pollutions reduced by the chosen methods and use social framing to make it more effective
Gemini API / Google AI Studio

We used Gemini as a way to analyze the users preference through tuning the model to specifically ask case-based questions which then leads to the method-recommendations
General

We used Flask, Python, and Javascript for most of the project.
What's next for ReduceNow

This is a very simple version, but I think the principle of it can be scaled widely to help make incremental changes for people to be more sustainable. For instance, in companies, it can be used to help find the easiest and most cost-effective ways for processes or employees to reduce their emissions. Or it can be implemented in educational institutions to help build the sustainable habit.

###Challenges we ran into

Initially we wanted to add a voice component to as an option, but ran into an issue with pyaudio and audio playback, therefore we had to scrap it. Additionally it's my first solo project on a hackathon so finishing everything was a huge personal accomplishment haha.

