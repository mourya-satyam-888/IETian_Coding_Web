
	        "use strict";

	        var editor = null;


	        $(document).ready(function () {
				$('#custom_input').css('display','none');
				$('#run').css('display','none');
	            require(['vs/editor/editor.main'], function () {
	                var MODES = (function () {
	                    var modesIds = monaco.languages.getLanguages().map(function (lang) {
	                        return lang.id;
	                    });
	                    modesIds.sort();

	                    return modesIds.map(function (modeId) {
	                        return {
	                            modeId: modeId,
	                            sampleURL: 'index/samples/sample.' + modeId + '.txt'
	                        };
	                    });
	                })();



	                var startModeIndex = 5;
	                for (var i = 0; i < MODES.length; i++) {
	                    var o = document.createElement('option');
	                    o.textContent = MODES[i].modeId;
	                    if (i == 5) {
	                        o.textContent = 'C';
	                        $(".language-picker").append(o);
	                    }
	                    if (i == 9) {
	                        o.textContent = 'C++';
	                        $(".language-picker").append(o);
	                    }
                        if (i == 20) {
	                        o.textContent = 'JAVA';
	                        $(".language-picker").append(o);
	                    }
	                    if (i == 41) {
	                        o.textContent = 'PYTHON3';
	                        $(".language-picker").append(o);
	                    }





	                }




                    $(document).on('submit','#code_form',function(e){
                    e.preventDefault();
					if(window.editor == null)
					return;
					$('#run').css('display','block');
					$('#result').css('display','none')
					$('.btnn').prop('disabled',true);
                    $.ajax({
                            type:'post',
                            url:'runcode/',
                            data:{
                                language:$(".language-picker").val(),
                                code:window.editor.getValue(),
                                custom_input:$('#custom_input').val(),
                                csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
                            },
                            success:function(json)
                            {
                                $('#run').css('display','none');
								$('.btnn').prop('disabled',false);
								$('#result').css('display','block');
								$('#result').html(json.response);
                                console.log("Success");

                            }

                        });
                });





	                $(".language-picker")[0].selectedIndex = 0;


	                $(".language-picker").change(function () {


	                    if ($(".language-picker").val() == 'C')
							{loadSample(MODES[5]);
							$('#result').css('display','none')
							$('#custom_input').css('display','block');
							$('#custom_input').val('')='';

							}

	                    else if ($(".language-picker").val() == 'C++')
						    {
	                        loadSample(MODES[9]);

							$('#custom_input').css('display','block');
							$('#custom_input').val('');
							$('#result').css('display','none')
							}

	                    else if ($(".language-picker").val() == 'JAVA')
						   {
	                        loadSample(MODES[20]);

							$('#custom_input').css('display','block');
							$('#custom_input').val('');
							$('#result').css('display','none')
							}
	                    else if ($(".language-picker").val() == 'PYTHON3')
	                        {loadSample(MODES[41]);

							$('#custom_input').css('display','block');
							$('#custom_input').val('');
							$('#result').css('display','none')
							}
	                    else if ($(".language-picker").val() == 'select')
                            { loadSample(MODES[0]);

                            $('#custom_input').css('display','none');
							$('#custom_input').val('');
							$('#result').css('display','none')
							}




	                });

	                $(".theme-picker").change(function () {
	                    changeTheme(this.selectedIndex);
	                });




	            });

	            window.onresize = function () {
	                if (editor) {
	                    editor.layout();
	                }

	            };
	        });

	        var preloaded = {};
	        (function () {
	            var elements = Array.prototype.slice.call(document.querySelectorAll('pre[data-preload]'), 0);

	            elements.forEach(function (el) {
	                var path = el.getAttribute('data-preload');
	                preloaded[path] = el.innerText || el.textContent;
	                el.parentNode.removeChild(el);
	            });
	        })();

	        function xhr(url, cb) {
	            if (preloaded[url]) {
	                return cb(null, preloaded[url]);
	            }
	            $.ajax({
	                type: 'GET',
	                url: url,
	                dataType: 'text',
	                error: function () {
	                    cb(this, null);
	                }
	            }).done(function (data) {
	                cb(null, data);
	            });
	        }

function loadSample(mode) {
	$('.loading.editor').show();
	xhr(mode.sampleURL, function(err, data) {
		if (err) {
			if (editor) {
				if (editor.getModel()) {
					editor.getModel().dispose();
				}
				editor.dispose();
				editor = null;
			}
			$('.loading.editor').fadeOut({ duration: 200 });
			$('#editor').empty();
			$('#editor').append('<p class="alert alert-error">Select a language to code</p>');
			return;
		}

		if (!editor) {
			$('#editor').empty();
			editor = monaco.editor.create(document.getElementById('editor'), {
				model: null,
			});
		}

		var oldModel = editor.getModel();
		var newModel = monaco.editor.createModel(data, mode.modeId);
		editor.setModel(newModel);
		if (oldModel) {
			oldModel.dispose();
		}
		$('.loading.editor').fadeOut({ duration: 300 });
	})
}


	        function changeTheme(theme) {
	            var newTheme = (theme === 1 ? 'vs-dark' : (theme === 0 ? 'vs' : 'hc-black'));
	            monaco.editor.setTheme(newTheme);
	        }