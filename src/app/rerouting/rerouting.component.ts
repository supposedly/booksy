import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { Globals } from '../globals';

@Component({
  selector: 'app-rerouting',
  template: '',
  styles: ['']
})
export class ReroutingComponent implements OnInit {
  constructor(
    private globals: Globals,
    private router: Router,
    private route: ActivatedRoute
  ) {}
  ngOnInit() {
    if (this.globals.isLoggedIn) {
      this.router.navigate(['home']);
    }
    setTimeout(
      () => {
        this.router.navigate(['/']);
      },
    500);
    // Guess that counts as a 'stupid hack' -- its purpose is just to delay the redirection
    // so that the requisite setup stuff can happen (because without that 500ms delay, this
    // will try to do its thing first and end up with a blank sidebar amid other fun things
    
    this.router.navigateByUrl(this.route.snapshot.queryParams['redirect'] || '/login', {});
    //TODO: See if you can figure out how to make it redirect like it should...
  }

}
