from collections import defaultdict
from statistics import mean

class TaiXiuPredictor:
    def __init__(self):
        self.history = []
        self.predictions = []
        self.correct = 0
        self.incorrect = 0
        self.markov_cache = {}
        self.last_pattern = None

    def add_result(self, result):  # result: 'tài' hoặc 'xỉu'
        if result not in ['tài', 'xỉu']:
            return

        if len(self.history) >= 3:
            current_prediction, _ = self.predict()
            self.predictions.append((result, current_prediction))
            if result == current_prediction:
                self.correct += 1
            else:
                self.incorrect += 1

        self.history.append(result)

    def detect_pattern(self):
        results = self.history
        if len(results) < 3:
            return {'type': 'none', 'desc': 'Cần ít nhất 3 kết quả', 'confidence': 0.0}
        
        last_three = results[-3:]
        if all(r == last_three[0] for r in last_three):
            return {'type': 'bệt', 'desc': f"bệt {last_three[0]}", 'confidence': 0.8}
        
        if len(results) >= 4 and all(results[i] != results[i-1] for i in range(1, min(len(results), 6))):
            return {'type': '1-1', 'desc': '1-1 (Tài-Xỉu xen kẽ)', 'confidence': 0.75}

        last_four = results[-4:]
        if last_four in [['tài','tài','xỉu','xỉu'], ['xỉu','xỉu','tài','tài']]:
            return {'type': '2-2', 'desc': '2-2 (2 Tài - 2 Xỉu)', 'confidence': 0.7}

        return {'type': 'random', 'desc': 'ngẫu nhiên', 'confidence': 0.5}

    def calculate_markov(self):
        results = self.history
        if len(results) < 3:
            return {'probTai': 50, 'probXiu': 50}

        last_two = ','.join(results[-2:])
        if last_two in self.markov_cache:
            return self.markov_cache[last_two]

        transitions = defaultdict(lambda: {'tài': 0, 'xỉu': 0})
        for i in range(len(results) - 2):
            key = f"{results[i]},{results[i+1]}"
            next_val = results[i+2]
            transitions[key][next_val] += 1

        total = sum(transitions[last_two].values())
        if total == 0:
            probs = {'probTai': 50, 'probXiu': 50}
        else:
            probs = {
                'probTai': transitions[last_two]['tài'] / total * 100,
                'probXiu': transitions[last_two]['xỉu'] / total * 100
            }

        self.markov_cache[last_two] = probs
        return probs

    def simple_decision_tree(self):
        if len(self.history) < 10:
            return None

        data = []
        labels = []
        for i in range(5, len(self.history)):
            seg = self.history[i-5:i]
            features = [
                seg.count('tài') / 5,
                seg.count('xỉu') / 5,
                self.detect_pattern()['confidence'],
                int(seg[-1] == seg[-2]),
                int(seg[-1] == 'tài')
            ]
            data.append(features)
            labels.append(1 if self.history[i] == 'tài' else 0)

        # Huấn luyện cây đơn giản (majority rule)
        if not data or not labels:
            return None
        last_features = data[-1]
        majority = 1 if mean(labels) > 0.5 else 0
        return {'prediction': 'tài' if majority == 1 else 'xỉu', 'confidence': 0.9}

    def predict(self):
        if len(self.history) < 3:
            return 'không rõ', 0

        pattern_info = self.detect_pattern()
        markov_probs = self.calculate_markov()
        dt_result = self.simple_decision_tree()

        dt_weight = 0.5 if dt_result else 0
        pattern_weight = 0.4
        markov_weight = 0.2

        pattern_pred = None
        if pattern_info['type'] in ['bệt', '1-1', '2-2']:
            last = self.history[-1]
            pattern_pred = 'xỉu' if last == 'tài' else 'tài'

        # Tổng hợp kết quả
        if dt_result and dt_result['confidence'] > pattern_info['confidence']:
            final = dt_result['prediction']
            confidence = dt_result['confidence'] * dt_weight
        elif pattern_pred:
            final = pattern_pred
            confidence = pattern_info['confidence'] * pattern_weight
        else:
            final = 'tài' if markov_probs['probTai'] > markov_probs['probXiu'] else 'xỉu'
            confidence = max(markov_probs['probTai'], markov_probs['probXiu']) / 100 * markov_weight

        final_confidence = round(min(95, max(50, confidence * 100)), 1)
        return final, final_confidence

# Ví dụ sử dụng
if __name__ == '__main__':
    p = TaiXiuPredictor()
    for r in ['tài', 'xỉu', 'tài', 'xỉu', 'tài', 'tài', 'tài', 'xỉu', 'tài', 'xỉu']:
        p.add_result(r)

    prediction, confidence = p.predict()
    print(f"Dự đoán tiếp theo: {prediction.upper()} ({confidence}%)")
