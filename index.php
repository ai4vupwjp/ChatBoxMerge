<?php
// php -S 127.0.0.1:8000
// php -S 36.228.153.206:8000
// 共通 session_id
session_id('b9jc4kekq6idnvsjdo7sf57t3f');
$result = session_start();
// 簡單驗證
$return_data = [];
$return_data['session_id'] = session_id();
header('Access-Control-Allow-Origin: *');

if (count(array_diff_key(['op_code'=>null, 'data'=>null], $_POST)) > 0) {
    $return_data['op_result'] = -1;
    $return_data['post'] = $_POST;
    $return_data['op_code'] = null;
    echo json_encode ($return_data);
    return;
}

if ($_POST['op_code'] === 'add_message') {
    if (array_key_exists('message_list', $_SESSION) === false) {
        $_SESSION['message_list'] = [];
        $_SESSION['score_list'] = [];
        $_SESSION['nickname_list'] = [];
    }
    list ($nickname, $message, $source) = json_decode ($_POST['data'], true);
    $_SESSION['nickname_list'][] = $nickname;
    $_SESSION['message_list'][] = $message;
    $_SESSION['score_list'][] = $source;

    $return_data['op_code'] = 'add_message';
    $return_data['nickname_list'] = $_SESSION['nickname_list'];
    $return_data['message_list'] = $_SESSION['message_list'];
    $return_data['score_list'] = $_SESSION['score_list'];
    echo json_encode ($return_data);
    return;
}

if ($_POST['op_code'] === 'get_message') {
    // $return_data['message_list'] = $_SESSION['message_list'];
    // $_POST['data']
    $return_data['nickname_list'] = [];
    $return_data['message_list'] = [];
    $return_data['score_list'] = [];
    $return_data['op_code'] = 'get_message';
    if (array_key_exists('message_list', $_SESSION) === false) {
        echo json_encode ($return_data);
        return;
    }
    if (count ($_SESSION['message_list']) == $_POST['data']) {
        echo json_encode ($return_data);
        return;
    }
    if (count ($_SESSION['message_list']) < $_POST['data']) {
        $return_data['op_code'] = 'clean_message';
        echo json_encode ($return_data);
        return;
    }
    $return_data['nickname_list'] = array_slice($_SESSION['nickname_list'], $_POST['data']);
    $return_data['message_list'] = array_slice($_SESSION['message_list'], $_POST['data']);
    $return_data['score_list'] = array_slice($_SESSION['score_list'], $_POST['data']);
    // 不清除的做法
    // $_SESSION['nickname_list'] = [];
    // $_SESSION['message_list'] = [];
    // $_SESSION['score_list'] = [];
    echo json_encode ($return_data);
    return;
}

if ($_POST['op_code'] === 'clean_session') {
    session_destroy();
    $return_data['session_data'] = $_SESSION;
    $return_data['op_code'] = $_POST['op_code'];
    echo json_encode ($return_data);
    return;
}
