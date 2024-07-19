var getCaptherUrl = "https://sec.biliapi.net/th/captcha/get";
var validateCaptherUrl = "https://sec.biliapi.net/th/captcha/check";
var getIPUrl = "https://security.bilibili.com/412";
var checkUrl = "https://sec.biliapi.net/th/captcha/cc/check";

window.onload = function () {
  datetime_now = new Date();
  $(".user_url").text("当前URL：" + location.href);
  $(".datetime_now").text("当前时间：" + datetime_now.toLocaleString());
  // 获取并显示客户端的 IP 地址 & mid
  $.ajax({
    url: getIPUrl,
    async: true,
    xhrFields: {
      withCredentials: true,
    },
    success: function (data) {
      $(".user_ip").text("IP地址：" + data.data.ip_addr);
      $(".user_id").text("用户ID：" + data.data.mid);
    },
  });
  // 获取验证码
  $.ajax({
    url: getCaptherUrl,
    // async: true,
    success: function (data) {
      if (data.data.show === true) {
        addDom(data);

        $("#img-captcha").click(function () {
          var tmp_data = getCaptcha();
          $("#img-captcha").attr("src", function () {
            return genImg(tmp_data.data.captcha.imageBase64String);
          });
          $("#hidden-input").val(tmp_data.data.captcha.token);
        });

        $("#validate_submit").click(function () {
          var hidden_v = $("#hidden-input").val();
          var input_v = $("#validate-input").val();
          var post_data = {
            token: hidden_v,
            key: input_v,
          };
          $.ajax({
            url: validateCaptherUrl,
            type: "POST",
            data: post_data,
            async: false,
            contentType: "application/x-www-form-urlencoded",
            success: function (data) {
              if (data.code === 0) {
                // 设置10秒后跳转 给解封一点时间
                setTimeout(function () {
                  location.reload();
                }, 10000);

                $("#success_msg").show();
                $("#error_msg").hide();
              } else {
                // 刷新验证码，显示错误信息
                var tmp_data = getCaptcha();
                $("#img-captcha").attr("src", function () {
                  return genImg(tmp_data.data.captcha.imageBase64String);
                });
                $("#hidden-input").val(tmp_data.data.captcha.token);

                $("#error_msg").show();
                $("#success_msg").hide();
              }
            },
          });
        });
      }
    },
    timeout: 100,
  });
  // 解析 cookie ，判断 cookie 中 cc 的部分，判断是否需要拉取 cc 相关资源
  if (isSecTokenExisted()) {
    handleSecToken();
  }
};

function genImg(data) {
  return "data:image/jpeg;base64," + data;
}

function getCaptcha() {
  var resp = {};
  $.ajax({
    url: getCaptherUrl,
    async: false,
    success: function (data) {
      resp = data;
    },
    timeout: 5000,
  });
  return resp;
}

function addDom(data) {
  // 创建 label
  $(".check-input .title").append(
    '<div class="txt-item">请输入验证码进行人机校验:</div>'
  );

  // 创建 img
  var captcha_img = new Image();
  captcha_img.src = genImg(data.data.captcha.imageBase64String);
  captcha_img.id = "img-captcha";
  var rp = document.getElementsByClassName("check-input");
  $(".check-input .box-pic").append(captcha_img);

  // 创建 hidden input value
  var hidden_value = document.createElement("input");
  hidden_value.value = data.data.captcha.token;
  hidden_value.id = "hidden-input";
  hidden_value.setAttribute("type", "hidden");
  $(".check-input").append(hidden_value);

  // 创建 validate input value
  $(".check-input .box").append('<input id="validate-input"></input>');

  // 创建 提交 button
  $(".check-input .box").append('<button id="validate_submit">提交</button>');

  $(".check-input .state").append(
    '<span id="success_msg" style="color: green; display: none;">验证成功，5s后自动刷新页面....</span>'
  );
  $(".check-input .state").append(
    '<span id="error_msg" style="color: red; display: none;">验证码错误</span>'
  );
}

function handleSecToken() {
  // 解析 cookie ，判断 cookie 中 cc 的部分，判断是否需要拉取 cc 相关资源
  // 获取题目后，进行算力挑战
  // 运算完成后，将结果发送到 验证服务中
  // 跳转到来之前的页面
  // type 1=直接拦截 2=验证码 3=算力挑战 4=脑电波检测
  let tokens = Cookies.get("X-BILI-SEC-TOKEN").split(",");
  let type = tokens[0];
  let sec_token = tokens[1];
  if (type == "3") {
    $(".err-text").css("color", "#03a9f4");
    $(".err-text").text("正在识别风险中...请稍等大约10秒...");
    let payload = sec_token.split(".")[1];
    let raw_data = "";
    try {
      raw_data = JSON.parse(base64decode(payload));
    } catch (error) {
      Cookies.remove("X-BILI-SEC-TOKEN");
      return;
    }
    let q = raw_data["q"];
    let r = raw_data["r"];
    let type = raw_data["type"];
    let verity = raw_data["verity"];
    let exp = raw_data["exp"];
    let currentTs = parseInt(new Date().valueOf() / 1000);
    if (currentTs > exp) {
      Cookies.remove("X-BILI-SEC-TOKEN");
      return;
    }
    if (verity == 0) {
      pow(q, r, type);
    } else {
      console.log("skip checking sec token, verity is : " + verity);
      $(".err-text").text("已成功验证,请刷新重试");
    }
  }
}

function isSecTokenExisted() {
  if (document.cookie.indexOf("X-BILI-SEC-TOKEN=") == -1) {
    return false;
  } else {
    return true;
  }
}

function base64decode(data) {
  return window.atob(data);
}

function pow(q, r, type) {
  let result = "";
  if (type == "1") {
    result = pow1(q, r);
    // 找到结果以后，发送数据到验证服务中
    checkToken(result);
    return true;
  } else {
    return false;
  }
}

function pow1(q, r) {
  let range = 5_000_000;
  for (let i = 0; i < range; i++) {
    if (sha256(q + i) == r) {
      return i;
    }
  }
}

/**
 * 发送待验证的 算力验证结果到检测服务中，如果检查成功，则设置 cookie
 */
function checkToken(result) {
  let payload = {
    token: Cookies.get("X-BILI-SEC-TOKEN").split(",")[1],
    result: result,
  };
  $.ajax({
    url: checkUrl,
    data: payload,
    type: "POST",
    async: false,
    contentType: "application/x-www-form-urlencoded",
    success: function (data) {
      // 设置 cookie
      if (data["code"] == 0) {
        document.cookie = "X-BILI-SEC-TOKEN=" + data["message"];
        $(".err-text").text("验证成功，请刷新页面");
      } else {
        // 更改页面内容，
        $(".err-text").text("* 自动验证失败，请重新刷新页面 *");
      }
    },
  });
}

function createScript(name) {
  var script = document.createElement("script");
  script.type = "text/javascript";
  script.src = name;
  document.getElementsByTagName("head")[0].appendChild(script);
}
