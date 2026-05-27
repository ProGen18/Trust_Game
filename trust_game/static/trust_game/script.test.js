/**
 * @jest-environment jsdom
 */

// c'est pénible de tester les fonctions avec oTree -> conflit back-end front-end
// donc ce fichier test doit être mis à jour à chaque modification de script.js

// Fonction pour mettre à jour le timer du chat
function updateChatTimer() {
  updateTimeRemaining();
  document.getElementById("time_remaining").textContent = timeRemaining;

  if (timeRemaining <= 0) {
    clearInterval(chatTimer);
    disableChat(true);
  }
}

function updateTimeRemaining() {
  const now = Date.now() / 1000;
  timeRemaining = Math.max(parseInt(expireTime - now), 0);
}

// Fonction pour désactiver le chat
function disableChat(is_expired) {
  // is_expired : boolean = true si temps écoulé, faux si c'est le joueur A qui a envoyé
  const placeholder = is_expired
    ? "Temps écoulé"
    : "Joueur A a pris sa décision";
  if (has_cheap_talk) setDisabled(inputCheapTalk, buttonCheapTalk, placeholder);

  if (has_chat_gpt) setDisabled(inputGPT, buttonGPT, placeholder);
}
// désactive les composants du chat
function setDisabled(input, button, placeholder) {
  input.disabled = true;
  button.disabled = true;
  input.placeholder = placeholder;
}

// Fonctions pour envoyer un message
function sendChatMessageCheapTalk(message) {
  playerPrefix = roleIsPlayerA ? "Joueur A" : "Joueur B";
  if (isTyping) doneTyping();

  return { message: message, player_type: playerPrefix };
}

function sendChatMessageGPT(message, playerPrefix) {
  const chatBoxGPT = document.getElementById("chatbox-gpt");
  const messageHTML = `${playerPrefix}${message}<br>`;
  chatBoxGPT.innerHTML += messageHTML;
  chatBoxGPT.scrollTop = chatBoxGPT.scrollHeight;

  return { message: message, is_chat_gpt: true };
}

// playerPrefix nécessaire en cas d'appel pour chatgpt
function sendChatMessage(input, playerPrefix = null) {
  const message = input.value.trim();
  let dataToSend;

  if (!message) return;

  if (playerPrefix == null) dataToSend = sendChatMessageCheapTalk(message);
  else dataToSend = sendChatMessageGPT(message, playerPrefix);

  input.value = "";
  input.focus();

  liveSend(dataToSend);
}

// reconstruis les data et les envoie en cas de refresh
function refreshFromSavedData() {
  const amount_sent = js_vars.amount_sent;
  const amount_sent_back = js_vars.amount_sent_back;

  if (amount_sent != null) {
    disableChat(false);
    const data_sent = { status: "sent", amount_sent: amount_sent };
    const data_received = {
      status: "received",
      amount_sent: amount_sent,
      tripled_amount: amount_sent * js_vars.multiplier,
    };
    liveRecv(data_sent);
    liveRecv(data_received);
  }

  if (amount_sent_back != null) {
    const data_complete = {
      status: "complete",
      can_proceed: true,
      amount_sent: amount_sent,
      amount_sent_back: amount_sent_back,
      tripled_amount: amount_sent * js_vars.multiplier,
    };
    liveRecv(data_complete);
  }
}
// fonctions d'envoi de€
function sendTokens() {
  const amountInput = document.getElementById("amount_input");
  const amount = parseInt(amountInput.value);

  if (isNaN(amount) || amount < 0 || amount > js_vars.endowment) {
    amountInput.classList.add("is-invalid");
    return;
  }

  amountInput.classList.remove("is-invalid");
  liveSend({ amount_sent: amount });

  document.getElementById("send_button").disabled = true;
  document.getElementById("sent_amount").textContent = amount;
  document.getElementById("waiting_message").classList.remove("d-none");
}

function sendTokensBack() {
  const amountBackInput = document.getElementById("amount_back_input");
  const maxAmount = parseInt(
    document.getElementById("tripled_amount_1").textContent
  );
  const amountBack = parseInt(amountBackInput.value);

  if (isNaN(amountBack) || amountBack < 0 || amountBack > maxAmount) {
    amountBackInput.classList.add("is-invalid");
    return;
  }

  amountBackInput.classList.remove("is-invalid");
  liveSend({ amount_sent_back: amountBack });
  document.getElementById("send_back_button").disabled = true;
}

// Fonction pour mettre à jour les résultats finaux

function resultsPlayerA(data) {
  const resultsDiv = document.getElementById("final_results_content");
  const amountSent = data.amount_sent;
  const amountReceived = data.amount_sent_back;
  const finalBalance = js_vars.endowment - amountSent + amountReceived;

  resultsDiv.innerHTML = `
        <p>Vous avez envoyé ${amountSent}€ au Joueur B.</p>
        <p>Le Joueur B vous a renvoyé ${amountReceived}€.</p>
        <p><strong>Votre solde final: ${finalBalance}€</strong></p>
      `;
}

function resultsPlayerB(data) {
  const resultsDiv = document.getElementById("final_results_content");
  const amountReceived = data.amount_sent;
  const tripledAmount = data.tripled_amount;
  const amountSentBack = data.amount_sent_back;
  const finalBalance = tripledAmount - amountSentBack;

  resultsDiv.innerHTML = `
        <p>Vous avez reçu ${tripledAmount}€ (${amountReceived} × ${js_vars.multiplier}).</p>
        <p>Vous avez renvoyé ${amountSentBack}€ au Joueur A.</p>
        <p><strong>Votre solde final: ${finalBalance}€</strong></p>
      `;
}

function updateFinalResults(data) {
  if (roleIsPlayerA) resultsPlayerA(data);
  else resultsPlayerB(data);
}

// Gestion des messages live

function handleChatGPTReply(data) {
  const chatBoxGPT = document.getElementById("chatbox-gpt");
  const reply = data.reply;
  chatBoxGPT.innerHTML += `${data.bot_prefix}${reply}<br>`;
  chatBoxGPT.scrollTop = chatBoxGPT.scrollHeight;
}

function handleNewMessage(data) {
  const chatHistory = document.getElementById("chat_history");
  const newMessage = data.new_message;

  chatHistory.innerHTML += newMessage;
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function handleTypingIndicator(data) {
  const typingIndicator = document.getElementById("typing_indicator");
  if (data.other_player_typing) {
    typingIndicator.classList.remove("d-none");
  } else {
    typingIndicator.classList.add("d-none");
  }
}

function handleSentStatus(data) {
  disableChat(false);
  document.getElementById("send_button").disabled = true;
  document.getElementById("sent_amount").textContent = data.amount_sent;
  document.getElementById("waiting_message").classList.remove("d-none");
}

function handleReceivedStatus(data) {
  disableChat(false);
  document.getElementById("waiting_for_A").classList.add("d-none");
  document.getElementById("received_amount_display").classList.remove("d-none");
  document.getElementById("received_amount").textContent = data.amount_sent;
  document.getElementById("tripled_amount_1").textContent = data.tripled_amount;
  document.getElementById("tripled_amount_2").textContent = data.tripled_amount;
  document.getElementById("amount_back_input").max = data.tripled_amount;
}

function handleCompleteStatus(data) {
  canProceed = data.can_proceed;
  document.getElementById("game_results").classList.remove("d-none");
  updateFinalResults(data);
  if (canProceed) document.getElementById("proceed_button").disabled = false;
}

function liveRecv(data) {
  if (data.is_chat_gpt) handleChatGPTReply(data);
  if (data.new_message) handleNewMessage(data);
  if (data.hasOwnProperty("other_player_typing")) handleTypingIndicator(data);
  if (data.status === "sent" && roleIsPlayerA) handleSentStatus(data);
  if (data.status === "received" && !roleIsPlayerA) handleReceivedStatus(data);
  if (data.status === "sent" || data.status === "received")
    document.getElementById("time").classList.add("d-none");
  if (data.status === "complete") handleCompleteStatus(data);
}

// simule les variables globales
let has_cheap_talk = true;
let has_chat_gpt = true;

let inputCheapTalk;
let buttonCheapTalk;

let inputGPT;
let buttonGPT;

let roleIsPlayerA = true;
let isTyping = false;

let doneTypingCalled = false;
let liveSendData = null;
let canProceed = false;

// fonctions mockées
function doneTyping() {
  doneTypingCalled = true;
}

function liveSend(data) {
  liveSendData = data;
}

let js_vars = null;

// ces fonctions créent des élements DOM pour mener les tests
function createElement(tag, id, className = "") {
  const element = document.createElement(tag);
  element.id = id;
  element.className = className;
  document.body.appendChild(element);
  return element;
}

function createChatBoxElement(tag, id, innerHTML, scrollTop, scrollHeight) {
  const element = document.createElement(tag);
  element.id = id;
  element.innerHTML = innerHTML;
  element.scrollTop = scrollTop;
  // scrollHeight est en lecture seule donc on le mock
  Object.defineProperty(element, "scrollHeight", {
    value: scrollHeight,
    configurable: true,
  });
  document.body.appendChild(element);
  return element;
}

afterEach(() => {
  document.body.innerHTML = "";
});

test("function setDisabled", () => {
  const input = { disabled: false, placeholder: "" };
  const button = { disabled: false };
  const placeholder = "Ceci est un placeholder";

  setDisabled(input, button, placeholder);

  expect(input.disabled).toBe(true);
  expect(input.placeholder).toBe(placeholder);
  expect(button.disabled).toBe(true);
});

test("function disableChat true", () => {
  inputCheapTalk = { disabled: false, placeholder: "" };
  buttonCheapTalk = { disabled: false };

  inputGPT = { disabled: false, placeholder: "" };
  buttonGPT = { disabled: false };

  disableChat(true);

  expect(inputCheapTalk.disabled).toBe(true);
  expect(inputCheapTalk.placeholder).toBe("Temps écoulé");
  expect(buttonCheapTalk.disabled).toBe(true);

  expect(inputGPT.disabled).toBe(true);
  expect(inputGPT.placeholder).toBe("Temps écoulé");
  expect(buttonGPT.disabled).toBe(true);
});

test("function disableChat false", () => {
  inputCheapTalk = { disabled: false, placeholder: "" };
  buttonCheapTalk = { disabled: false };

  inputGPT = { disabled: false, placeholder: "" };
  buttonGPT = { disabled: false };

  disableChat(false);

  expect(inputCheapTalk.disabled).toBe(true);
  expect(inputCheapTalk.placeholder).toBe("Joueur A a pris sa décision");
  expect(buttonCheapTalk.disabled).toBe(true);

  expect(inputGPT.disabled).toBe(true);
  expect(inputGPT.placeholder).toBe("Joueur A a pris sa décision");
  expect(buttonGPT.disabled).toBe(true);
});

test("function sendChatMessage Cheap Talk", () => {
  const input = {
    value: " Ceci est une valeur de test !   ",
    focus: () => {
      input.focused = true;
    },
    focused: false,
  };
  liveSendData = null;
  isTyping = true;
  doneTypingCalled = false;
  roleIsPlayerA = true;

  sendChatMessage(input);

  expect(liveSendData.message).toBe("Ceci est une valeur de test !");
  expect(liveSendData.player_type).toBe("Joueur A");
  expect(input.value).toBe("");
  expect(input.focused).toBe(true);
  expect(doneTypingCalled).toBe(true);
});

test("function sendChatMessage ChatGPT", () => {
  const input = {
    value: " Ceci est une valeur de test !   ",
    focus: () => {
      input.focused = true;
    },
    focused: false,
  };

  const fakeChatBoxGPT = createChatBoxElement(
    "div",
    "chatbox-gpt",
    "Ancien: Message<br>",
    0,
    1000
  );

  liveSendData = null;

  sendChatMessage(input, "Toto: ");

  expect(liveSendData.message).toBe("Ceci est une valeur de test !");
  expect(liveSendData.is_chat_gpt).toBe(true);
  expect(input.value).toBe("");
  expect(input.focused).toBe(true);
  expect(fakeChatBoxGPT.innerHTML).toBe(
    "Ancien: Message<br>Toto: Ceci est une valeur de test !<br>"
  );
  expect(fakeChatBoxGPT.scrollTop).toBe(1000);
});

test("function sendChatMessage message vide", () => {
  const input = {
    value: "    ",
    focus: () => {
      input.focused = true;
    },
    focused: false,
  };

  liveSendData = "ne va pas changer";

  sendChatMessage(input);
  expect(liveSendData).toBe("ne va pas changer");

  sendChatMessage(input, "Toto: ");
  expect(liveSendData).toBe("ne va pas changer");
});

test("function handleChatGPTReply", () => {
  const data = { reply: "Ceci est une réponse.", bot_prefix: "Robot: " };
  const innerHTML = "Ceci est une question.<br>";
  const fakeChatBoxGPT = createChatBoxElement(
    "div",
    "chatbox-gpt",
    innerHTML,
    0,
    500
  );

  handleChatGPTReply(data);

  expect(fakeChatBoxGPT.innerHTML).toBe(
    "Ceci est une question.<br>Robot: Ceci est une réponse.<br>"
  );
  expect(fakeChatBoxGPT.scrollTop).toBe(500);
});

test("function handleNewMessage", () => {
  const data = { new_message: "Ceci est un nouveau message !" };
  const innerHTML = "Ceci est un ancien message...";
  const fakeChatHistory = createChatBoxElement(
    "div",
    "chat_history",
    innerHTML,
    0,
    200
  );

  handleNewMessage(data);

  expect(fakeChatHistory.innerHTML).toBe(
    "Ceci est un ancien message...Ceci est un nouveau message !"
  );
  expect(fakeChatHistory.scrollTop).toBe(200);
});

test("function handleTypingIndicator typing", () => {
  const data = { other_player_typing: true };
  const fakeTypingIndicator = createElement(
    "div",
    "typing_indicator",
    "test-class d-none toto"
  );

  handleTypingIndicator(data);

  expect(fakeTypingIndicator.className).toBe("test-class toto");
});

test("function handleTypingIndicator not typing", () => {
  const data = { other_player_typing: false };
  const fakeTypingIndicator = createElement(
    "div",
    "typing_indicator",
    "test-class toto"
  );

  handleTypingIndicator(data);

  expect(fakeTypingIndicator.className).toBe("test-class toto d-none");
});

test("function handleSentStatus", () => {
  const data = { amount_sent: "30" };
  const fakeSendButton = createElement("button", "send_button");
  const fakeSentAmount = createElement("span", "sent_amount");
  const fakeWaitingMessage = createElement(
    "div",
    "waiting_message",
    "toto d-none"
  );

  handleSentStatus(data);

  expect(fakeSendButton.disabled).toBe(true);
  expect(fakeSentAmount.textContent).toBe("30");
  expect(fakeWaitingMessage.classList.contains("toto")).toBe(true);
  expect(fakeWaitingMessage.classList.contains("d-none")).toBe(false);
});

test("function handleReceivedStatus", () => {
  const data = { amount_sent: "5", tripled_amount: "15" };
  const fakeWaitingForA = createElement("div", "waiting_for_A", "toto");
  const fakeReceivedAmountDisplay = createElement(
    "div",
    "received_amount_display",
    "titi d-none"
  );
  const fakeReceivedAmount = createElement("span", "received_amount");
  const fakeTripledAmount1 = createElement("span", "tripled_amount_1");
  const fakeTripledAmount2 = createElement("span", "tripled_amount_2");
  const amountBackInput = createElement("input", "amount_back_input");
  amountBackInput.max = "0";

  handleReceivedStatus(data);

  expect(fakeWaitingForA.classList.contains("d-none")).toBe(true);
  expect(fakeReceivedAmountDisplay.classList.contains("titi")).toBe(true);
  expect(fakeReceivedAmountDisplay.classList.contains("d-none")).toBe(false);
  expect(fakeReceivedAmount.textContent).toBe(data.amount_sent);
  expect(fakeTripledAmount1.textContent).toBe(data.tripled_amount);
  expect(fakeTripledAmount2.textContent).toBe(data.tripled_amount);
  expect(amountBackInput.max).toBe(data.tripled_amount);
});

test("function resultsPlayerA", () => {
  const fakeFinalResultsContent = createElement("div", "final_results_content");
  const data = { amount_sent: 3, amount_sent_back: 1 };
  const expectedInnerHTML = `
        <p>Vous avez envoyé 3€ au Joueur B.</p>
        <p>Le Joueur B vous a renvoyé 1€.</p>
        <p><strong>Votre solde final: 3€</strong></p>
      `;
  roleIsPlayerA = true;
  js_vars = { endowment: 5 };

  resultsPlayerA(data);

  expect(fakeFinalResultsContent.innerHTML).toBe(expectedInnerHTML);
});

test("function resultsPlayerB", () => {
  const fakeFinalResultsContent = createElement("div", "final_results_content");
  const data = { amount_sent: 3, tripled_amount: 9, amount_sent_back: 1 };
  const expectedInnerHTML = `
        <p>Vous avez reçu 9€ (3 × 3).</p>
        <p>Vous avez renvoyé 1€ au Joueur A.</p>
        <p><strong>Votre solde final: 8€</strong></p>
      `;
  roleIsPlayerA = false;
  js_vars = { multiplier: 3 };

  resultsPlayerB(data);

  expect(fakeFinalResultsContent.innerHTML).toBe(expectedInnerHTML);
});

test("function sendTokens", () => {
  const fakeAmountInput = createElement("input", "amount_input");
  const fakeSendButton = createElement("button", "send_button");
  const fakeSentAmount = createElement("span", "sent_amount");
  const fakeWaitingMessage = createElement("div", "waiting_message", "d-none");

  fakeAmountInput.value = "99";
  js_vars = { endowment: 100 };
  liveSendData = null;

  sendTokens();

  expect(fakeSendButton.disabled).toBe(true);
  expect(fakeSentAmount.textContent).toBe("99");
  expect(liveSendData).toEqual({ amount_sent: 99 });
  expect(fakeWaitingMessage.classList.contains("is-invalid")).toBe(false);
});

test("function sendTokens amount NaN", () => {
  const fakeAmountInput = createElement("input", "amount_input");
  fakeAmountInput.value = "bonjour";
  js_vars = { endowment: 100 };

  sendTokens();

  expect(fakeAmountInput.classList.contains("is-invalid")).toBe(true);
});

test("function sendTokens amount < 0", () => {
  const fakeAmountInput = createElement("input", "amount_input");
  fakeAmountInput.value = "-8";
  js_vars = { endowment: 100 };

  sendTokens();

  expect(fakeAmountInput.classList.contains("is-invalid")).toBe(true);
});

test("function sendTokens amount > endowment", () => {
  const fakeAmountInput = createElement("input", "amount_input");
  fakeAmountInput.value = "9999";
  js_vars = { endowment: 100 };

  sendTokens();

  expect(fakeAmountInput.classList.contains("is-invalid")).toBe(true);
});

test("function sendTokensBack", () => {
  const fakeAmountBackInput = createElement("input", "amount_back_input");
  const fakeTripledAmount = createElement("input", "tripled_amount_1");
  const fakeSentBackButton = createElement("button", "send_back_button");

  fakeAmountBackInput.value = "79";
  fakeTripledAmount.textContent = "100";
  liveSendData = null;

  sendTokensBack();

  expect(fakeAmountBackInput.classList.contains("is-invalid")).toBe(false);
  expect(liveSendData).toEqual({ amount_sent_back: 79 });
  expect(fakeSentBackButton.disabled).toBe(true);
});

test("function sendTokensBack amountBack NaN", () => {
  const fakeAmountBackInput = createElement("input", "amount_back_input");
  const fakeTripledAmount = createElement("input", "tripled_amount_1");

  fakeAmountBackInput.value = "bonjour";
  fakeTripledAmount.textContent = "100";

  sendTokensBack();

  expect(fakeAmountBackInput.classList.contains("is-invalid")).toBe(true);
});

test("function sendTokensBack amountBack > tripledAmount", () => {
  const fakeAmountBackInput = createElement("input", "amount_back_input");
  const fakeTripledAmount = createElement("input", "tripled_amount_1");

  fakeAmountBackInput.value = "999";
  fakeTripledAmount.textContent = "100";

  sendTokensBack();

  expect(fakeAmountBackInput.classList.contains("is-invalid")).toBe(true);
});

test("function sendTokensBack amount < 0", () => {
  const fakeAmountBackInput = createElement("input", "amount_back_input");
  const fakeTripledAmount = createElement("input", "tripled_amount_1");

  fakeAmountBackInput.value = "-9";
  fakeTripledAmount.textContent = "100";

  sendTokensBack();

  expect(fakeAmountBackInput.classList.contains("is-invalid")).toBe(true);
});
