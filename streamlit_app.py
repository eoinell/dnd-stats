import streamlit as st
import numpy as np
from numpy.random import randint
import plotly.graph_objects as go
from plotly.subplots import make_subplots
st.header('Dungeons and Dragons Stats')

# different sided dice in DnD
sides = (4, 6, 8, 10, 12, 20)
dice = {'D'+ str(n) : n for n in sides} # D20 = 20 sided dice

cols = st.columns([10, 10, 7]) # layout stuff
with cols[0]:
    main_die = st.selectbox('Main Die', dice, index=5)
with cols[1]:
    # advantage means you get to roll twice and pick the higher roll, disadvantage the opposite
    advantage = st.radio('', ('Advantage', 'None', 'Disadvantage'), index=1) # 
with cols[2]:
    # static bonus applied to the roll
    modifier = int(st.number_input('Modifier', value=0, step=1, ))


# a bonus die can be added to some rolls, e.g. inspiration or guidance.
# sometimes its subtracted e.g. bane
additional_dice = []
dice_signs = []
more_dice_cols = st.columns([12,] + 5*[9])
with more_dice_cols[0]:
    number_more_dice = int(st.number_input('more dice', value=0, step=1, min_value=0, max_value=5))
for col, _ in zip(more_dice_cols[1:], range(number_more_dice)):
        with col:
            additional_dice.append(st.selectbox(f'extra die {len(additional_dice) + 1}', dice))
            dice_signs.append((1,-1)[st.checkbox('subtract', key=len(additional_dice))])



# target for the roll to be a 'success'


side = dice[main_die]
additional_sides = [dice[label] for label in additional_dice]
_min = sum([1,] + [a * s if s < 0 else 1 for a, s in zip(additional_sides, dice_signs)])
_max = sum([side,] + [a if s > 0 else s for a, s in zip(additional_sides, dice_signs)])
roll_range = np.arange(_min, _max + 1)
# additional dice subtracted changes the roll_range, but not the shape of the PDF (probability distribution function)
DC = st.slider('Difficulty Class', value=int(roll_range[len(roll_range)//2]), step=1, min_value=int(_min+modifier), max_value=int(_max+modifier), )

if advantage == 'Advantage':
    probs = np.array([2*(val - 1) + 1 for val in np.arange(1, side + 1)]) # base distribution
elif advantage == 'Disadvantage':
    probs = np.array([2*(side - val) + 1 for val in np.arange(1, side + 1)])
else:
    probs = np.ones(side) # all numbers equally probable if no advantage

for a_side in additional_sides:
    probs = np.convolve(probs, np.ones(a_side),) # convolve the PDFs

probs = probs / probs.sum()

x = roll_range + modifier # this deals with the modifier

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=x, y=[100*probs[i:].sum() for i in range(len(probs))], name="success %"),
    secondary_y=True,
)
fig.add_trace(
    go.Bar(x=x,y=100*probs, name='roll probability'),
    secondary_y=False,
)
fig.update_layout(
    title_text=""
)
fig.update_xaxes(title_text="DC")
fig.update_yaxes(title_text="Cumululative Probablility (%)", secondary_y=True)
fig.update_yaxes(title_text="Probability (%)", secondary_y=False)
fig.add_vline(x=DC, line_dash='dash', fillcolor='green')

cols = st.columns([10, 2])
with cols[0]:
    st.plotly_chart(fig, use_container_width=False)
with cols[1]:
    for _ in range(12):
        st.write(' ')
    st.metric('%',  round(100 * (probs * (x >= DC)).sum(), 2)) # if roll == DC success

cols = st.columns(3)

def rolled():
    val = randint(1, side) + sum([randint(1, s) for s in additional_sides])
    with cols[1]:
        st.subheader(f'{val}')
    with cols[2]:
        if val >= DC:
            st.markdown('<p style="font-family:Courier; color:Green; font-size: 20px;">Success ◉‿◉</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-family:Courier; color:Red; font-size: 20px;">Failure (╯︵╰,)</p>', unsafe_allow_html=True)
            
with cols[0]:
    st.button('Roll!', on_click=rolled)

'''
This page calculates the success probability of a skill check in Dungeons and Dragons and other similar dice-based games. This may be useful for DMs to get an idea of where to set the DC of a skill check to give the players an interesting chance. Often, guidance, advantage and modifiers can make it difficult to assess just what the odds are!


'''
