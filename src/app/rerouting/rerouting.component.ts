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
    // stupid hack
    // its purpose is just to delay the redirection by 500ms so that the requisite
    // setup stuff can happen in the meantime
    // (without this delay, a logged-in user will end up with amid other things a
    // totally-blank sidebar & a non-personalized checkout screen)
    
    this.router.navigateByUrl(this.route.snapshot.queryParams['redirect'] || '/login', {});
    // TODO: See if you can figure out how to make it redirect to the right page like it should...
  }

}
