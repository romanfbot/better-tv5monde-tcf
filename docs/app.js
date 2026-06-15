const state = {
  data: null,
  lot: null,
  question: null,
};

const els = {
  lotSelect: document.querySelector('#lotSelect'),
  questionSelect: document.querySelector('#questionSelect'),
  questionMeta: document.querySelector('#questionMeta'),
  questionTitle: document.querySelector('#questionTitle'),
  instruction: document.querySelector('#instruction'),
  imageBlock: document.querySelector('#imageBlock'),
  questionImage: document.querySelector('#questionImage'),
  audioBlock: document.querySelector('#audioBlock'),
  audio: document.querySelector('#audio'),
  audioLink: document.querySelector('#audioLink'),
  sourceLink: document.querySelector('#sourceLink'),
  answers: document.querySelector('#answers'),
  modelMeta: document.querySelector('#modelMeta'),
  transcript: document.querySelector('#transcript'),
};

init().catch((error) => {
  console.error(error);
  els.questionTitle.textContent = 'Failed to load TCF data';
  els.transcript.textContent = String(error?.message || error);
});

async function init() {
  const response = await fetch('./data/tcf-lots.json');
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

  state.data = await response.json();
  state.lot = state.data.lots[0];
  state.question = state.lot.questions[0];

  fillLotSelect();
  fillQuestionSelect();
  render();

  els.lotSelect.addEventListener('change', () => {
    state.lot = state.data.lots.find((lot) => lot.id === els.lotSelect.value);
    state.question = state.lot.questions[0];
    fillQuestionSelect();
    render();
  });

  els.questionSelect.addEventListener('change', () => {
    state.question = state.lot.questions.find((question) => String(question.number) === els.questionSelect.value);
    render();
  });
}

function fillLotSelect() {
  els.lotSelect.replaceChildren(
    ...state.data.lots.map((lot) => new Option(`${lot.title}`, lot.id)),
  );
  els.lotSelect.value = state.lot.id;
}

function fillQuestionSelect() {
  els.questionSelect.replaceChildren(
    ...state.lot.questions.map((question) => {
      const hasAudio = question.audioUrl ? '🎧 ' : '';
      return new Option(`${hasAudio}Question ${question.number}`, String(question.number));
    }),
  );
  els.questionSelect.value = String(state.question.number);
}

function render() {
  const lot = state.lot;
  const question = state.question;

  els.questionMeta.textContent = `${question.skill} · question ${question.number}`;
  els.questionTitle.textContent = question.prompt || `Question ${question.number}`;
  els.instruction.textContent = question.instruction || '';
  els.sourceLink.href = lot.sourceUrl;

  if (question.imageUrl) {
    els.questionImage.src = question.imageUrl;
    els.imageBlock.hidden = false;
  } else {
    els.questionImage.removeAttribute('src');
    els.imageBlock.hidden = true;
  }

  if (question.audioUrl) {
    els.audio.src = question.audioUrl;
    els.audioLink.href = question.audioUrl;
    els.audioBlock.hidden = false;
  } else {
    els.audio.removeAttribute('src');
    els.audioBlock.hidden = true;
  }

  renderAnswers(question);
  renderTranscript(question);
}

function renderAnswers(question) {
  els.answers.replaceChildren(
    ...question.answers.map((answer) => {
      const item = document.createElement('div');
      item.className = `answer ${answer.correct ? 'correct' : ''}`;

      const code = document.createElement('strong');
      code.textContent = answer.code;

      const text = document.createElement('span');
      text.textContent = answer.text;

      item.append(code, text);
      if (answer.correct) {
        const badge = document.createElement('em');
        badge.textContent = 'Correct answer';
        item.append(badge);
      }
      return item;
    }),
  );
}

function renderTranscript(question) {
  const tx = question.transcription;
  if (!tx?.text) {
    els.modelMeta.textContent = 'Transcript unavailable';
    els.transcript.textContent = 'No transcript is available for this question.';
    return;
  }

  els.modelMeta.textContent = `Transcript · ${tx.model}`;
  els.transcript.replaceChildren(...splitTranscript(tx.text).map((part) => {
    const p = document.createElement('p');
    p.textContent = part;
    return p;
  }));
}

function splitTranscript(text) {
  return text
    .replace(/\s+(?=(?:A|B|C|D)\.\s)/g, '\n')
    .replace(/\s+(?=(?:Écoutez|Choisissez|Quand|Quelle|Pourquoi|Selon|De quoi|A quoi)\b)/g, '\n')
    .split(/\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}
