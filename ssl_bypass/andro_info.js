var accum = [];

function methods(the_class) {
    Java.perform(function() {
        try {
            var ref = Java.use(the_class);
        } catch(e) {
            console.log("-- Invalid full-name. Starting search. --");
            classes(the_class, true);
            if (accum.length) {
                var ref = accum[0];
                console.log("--> Assuming the use of " + ref);
            }
            else {
                console.log("-- ERROR: cannot find candidate for: " + the_class + " --");
                return;
            }
        }
        console.log("Methods & properties:\n=====================");
        var methods = Object.getOwnPropertyNames(ref.__proto__);
        for (var i in methods) console.log('\t' + methods[i]);
    });
};

function classes(pattern_, silent_find_one) {
    const pattern = pattern_.toLowerCase()
    if (!silent_find_one) console.log("Matching Classes:");
    Java.perform (function() {
        Java.enumerateLoadedClasses({
            // when a class is found send it to the client
            onMatch: function(className) {
                if (className.toLowerCase().search(pattern)>=0) {
                    accum.push(className);
                    if (!silent_find_one) console.log("\t" + className);
                }
            },
            // when we are done enumerating classes send "done" to the client
            onComplete: function() {
                console.log("-- Enumeration done. --");
            }
        });
    });
}

// Questo script deve essere editato automaticamente per sostituire THE_NAME
function method(cla) {
    Java.perform(function(){
        var imposs_sig = 'skdjvksdvkjkjdvdhkjsdvj'
        try{console.log(Java.use(cla).THE_NAME.overload(imposs_sig))}
        catch(e) {send(e.toString()); return;}
	// If we're here no exc. has been generated
    });
}

if (!Java.available)
    console.log("JAVA UNAVAIL. FOR THIS PROCESS");
else {
    rpc.exports = {
        meth:function(cla) {methods(cla);}, // methods list for the class
        over:function(cla,ignored) {method(cla);},  // overloads list for the method
        clas:function(pat) {classes(pat, false);}  // classes list
    };
};
