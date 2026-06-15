import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTS = ROOT / 'data' / 'tv5monde-58'

question_data = [
    (1, '441', 'Écoutez les 4 propositions. Choisissez celle qui correspond à l\'image et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'B', [('A','Réponse A'),('B','Réponse B'),('C','Réponse C'),('D','Réponse D')], 'https://apprendre.tv5monde.com/sites/apprendre.tv5monde.com/files/styles/large_720/public/tcf_question/TV159T3750I3880M2498.jpeg?itok=6JNEr262'),
    (2, '442', 'Écoutez les 4 propositions. Choisissez celle qui correspond à l\'image et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'A', [('A','Réponse A'),('B','Réponse B'),('C','Réponse C'),('D','Réponse D')], 'https://apprendre.tv5monde.com/sites/apprendre.tv5monde.com/files/styles/large_720/public/tcf_question/TV159T4904I5066M2849.jpeg?itok=1dDlZz19'),
    (3, '443', 'Écoutez les 4 propositions. Choisissez celle qui correspond à l\'image et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','Réponse A'),('B','Réponse B'),('C','Réponse C'),('D','Réponse D')], 'https://apprendre.tv5monde.com/sites/apprendre.tv5monde.com/files/styles/large_720/public/tcf_question/TV159T3741I3871M2484.jpeg?itok=hGfLL-xt'),
    (4, '444', 'Écoutez la question et les 4 réponses. Choisissez la réponse qui correspond à la question et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'A', [('A','Réponse A'),('B','Réponse B'),('C','Réponse C'),('D','Réponse D')], None),
    (5, '445', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'A', [('A','Il a fait des travaux dans une école.'),('B','Il a changé de lycée dernièrement.'),('C','Il a renvoyé de nombreux élèves.'),('D','Il a acheté un nouvel établissement.')], None),
    (6, '446', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','Elle a lieu dans le centre de la ville.'),('B','Elle est quasi totalement automatisée.'),('C','Elle connaît un succès grandissant.'),('D','Elle occupe une surface importante.')], None),
    (7, '447', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'D', [('A','Établir des codes communs.'),('B','Échanger sur des techniques.'),('C','Éditer un album international.'),('D','Faire découvrir le domaine.')], None),
    (8, '448', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','À ses nombreuses victimes.'),('B','Aux solutions à apporter.'),('C','À ses causes probables.'),('D','Aux réactions politiques.')], None),
    (9, '449', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'A', [('A','Le jury est composé de journalistes internationaux.'),('B','Les cinéastes en compétition viennent de toute l’Europe.'),('C','Les films projetés ont été diffusés sur Internet.'),('D','Les téléspectateurs élisent le meilleur comédien.')], None),
    (10, '450', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'D', [('A','De l’opportunité qu’elle a eue de prendre un nouveau départ.'),('B','Du manque de reconnaissance des grandes entreprises internationales.'),('C','Des facilités à l’embauche mises en place dans son pays d’accueil.'),('D','Des difficultés professionnelles rencontrées lors de son expatriation.')], None),
    (11, '451', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','Il assure sa notoriété et celle de ses acteurs.'),('B','Il lui a été remis lors d\'une cérémonie prestigieuse.'),('C','Il lui a été attribué par d’autres professionnels.'),('D','Il récompense le film dont elle est le plus fière.')], None),
    (12, '452', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','À ses méthodes de fabrication de briques.'),('B','À sa mine de métaux précieux.'),('C','À ses matériaux naturels de construction.'),('D','À son grand marché aux poissons.')], None),
    (13, '453', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'A', [('A','Celles qui ont été soutenues par l’État.'),('B','Celles spécialisées dans les petites entreprises.'),('C','Celles qui investissent dans les énergies fossiles.'),('D','Celles qui spéculent sur les matières premières.')], None),
    (14, '454', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'C', [('A','Elle crée à partir d’œuvres étrangères.'),('B','Elle traite souvent du thème de la virilité.'),('C','Elle est influencée par sa propre culture.'),('D','Elle aborde des thèmes contemporains.')], None),
    (15, '455', 'Écoutez le document sonore et la question. Choisissez la bonne réponse et cliquez sur le bouton correspondant.', 'Cliquez sur votre réponse', 'B', [('A','Le thème imposé est le dessin humoristique.'),('B','Les artistes s’expriment sur la même surface.'),('C','Les œuvres proviennent de différents pays.'),('D','Les participants effectuent un dessin en temps limité.')], None),
]

questions = []
for number, qid, instruction, prompt, correct, answers, image_url in question_data:
    transcript_path = TRANSCRIPTS / f'q{number:02d}-parakeet.json.txt'
    transcription = transcript_path.read_text(encoding='utf-8').strip()
    questions.append({
        'number': number,
        'questionId': qid,
        'skill': 'Compréhension orale',
        'instruction': instruction,
        'prompt': prompt,
        'audioUrl': f'https://apprendre.tv5monde.com/sites/apprendre.tv5monde.com/files/tcf_question/159-{number}.mp3',
        'imageUrl': image_url,
        'correctAnswer': correct,
        'answers': [{'code': code, 'text': text, 'correct': code == correct} for code, text in answers],
        'transcription': {
            'model': 'nvidia/parakeet-tdt-0.6b-v3',
            'language': 'fr',
            'text': transcription,
            'rawFile': f'data/tv5monde-58/q{number:02d}-parakeet.json'
        }
    })

payload = {
    'version': 2,
    'source': 'tv5monde-tcf',
    'lots': [{
        'id': 'tv5monde-tcf-58',
        'lotId': 58,
        'title': "TV5MONDE TCF training test — lot 58",
        'sourceUrl': 'https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id=58#tcf_header',
        'scrapeMethod': 'See docs/EXTRACTION.md',
        'transcriptionModel': 'nvidia/parakeet-tdt-0.6b-v3',
        'questions': questions,
    }]
}

out = ROOT / 'docs' / 'data' / 'tcf-lots.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'wrote {out} ({len(questions)} questions)')
