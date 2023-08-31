use std::env;
use std::process;

struct Config {
    token: Option<String>,
    domain: Option<String>,
    ipv6: bool,
    proxy: bool,
    debug: bool,
}

impl Config {
    fn new() -> Self {
        Config {
            token: None,
            domain: None,
            ipv6: false,
            proxy: false,
            debug: false,
        }
    }
}

fn string_colour(input_str: &str, colour: &str) -> String {
    match colour {
        "R" => format!("\x1B[91m{}\x1B[00m", input_str),
        "G" => format!("\x1B[92m{}\x1B[00m", input_str),
        "B" => format!("\x1B[94m{}\x1B[00m", input_str),
        "Y" => format!("\x1B[93m{}\x1B[00m", input_str),
        _ => input_str.to_string(),
    }
}

fn pad_string(input_string: &str, desired_length: usize) -> String {
    if input_string.len() >= desired_length {
        input_string[..desired_length].to_string()
    } else {
        let padding = " ".repeat(desired_length - input_string.len());
        format!("{}{}", input_string, padding)
    }
}

fn print_debug(message: &str, debug: bool) {
    if debug {
        println!("{}: {}", string_colour("Debug", "B"), message);
    }
}

fn print_help() {
    let pad = 17;

    println!("Specify a Cloudflare Access Token and a desired (sub)domain, and the application will assign ");
    print!("the record with your IP address.\n\n");
    println!("{}:", string_colour("Options", "Y"));
    println!("{} Your Cloudflare API token.", pad_string("-t, --token", pad));
    println!("{} You can get them from {}", pad_string("", pad), string_colour("https://dash.cloudflare.com/profile/api-tokens", "Y"));
    println!("{} Assign {} permission to the domain you wish to modify.", pad_string("", pad), string_colour("Zone.DNS", "Y"));
    println!("{} The FQDN you wish to create/update with the IP address.", pad_string("-d, --domain", pad));
    println!("{} Use Cloudflare Proxy for the domain", pad_string("-p, --proxy", pad));
    println!("{} Only impacts record {}, not {}.", pad_string("", pad), string_colour("creation", "Y"), string_colour("update", "Y"));
    println!("{} Assigns and updates an AAAA record with IPv6 instead.", pad_string("--ipv6", pad));
    println!("{} Will crash if the destination record is IPv4, and vice versa.", pad_string("", pad));
    println!("{} Enables verbose output.", pad_string("--debug", pad));
    println!("\n{} Display script version.", string_colour("-v, --version", "G"));
    println!("{} Displays this help information.", string_colour("-h, --help", "G"));
}

fn print_version() {
    println!("Cloudflare Dynamic DNS (CDDNS) by soup-bowl (code@soupbowl.io) - pre-alpha.");
    println!("Source: https://github.com/soup-bowl/cloudflare-dynamicdns/");
}

fn get_configs() -> Config {
    let mut conf = Config::new();

    conf.token = env::var("CF_TOKEN").ok();
    conf.domain = env::var("CF_DOMAIN").ok();
    conf.ipv6 = env::var("CF_IPV6").is_ok();
    conf.proxy = env::var("CF_PROXY").is_ok();

    if conf.token.is_none() || conf.domain.is_none() {
        let args: Vec<String> = env::args().collect();
        let mut opts = getopts::Options::new();
        
        opts.optflag("h", "help", "Print help");
        opts.optflag("v", "version", "Print version");
        opts.optflag("d", "debug", "Enable debug mode");
        opts.optflag("", "ipv6", "Enable IPv6");
        opts.optopt("t", "token", "Set token", "TOKEN");
        opts.optopt("d", "domain", "Set domain", "DOMAIN");
        opts.optflag("p", "proxy", "Enable proxy");
        
        let matches = match opts.parse(&args[1..]) {
            Ok(m) => m,
            Err(_) => {
                process::exit(1);
            }
        };
        
        if matches.opt_present("help") {
            print_help();
            process::exit(0);
        }
        
        if matches.opt_present("version") {
            print_version();
            process::exit(0);
        }
        
        if matches.opt_present("debug") {
            conf.debug = true;
        }
        
        if matches.opt_present("ipv6") {
            conf.ipv6 = true;
        }
        
        if let Some(token) = matches.opt_str("t") {
            conf.token = Some(token);
        }
        
        if let Some(domain) = matches.opt_str("d") {
            conf.domain = Some(domain);
        }
        
        if matches.opt_present("proxy") {
            conf.proxy = true;
        }
        
        if conf.token.is_none() || conf.domain.is_none() {
            println!("Error: You're missing either the token, or the domain\n");
            print_help();
            process::exit(2);
        }
    }

    conf
}

fn main() {
    let args: Vec<String> = env::args().collect();

	let conf = get_configs();

    for arg in args.iter() {
        println!("Found an arg: {}", arg);
    }
}
