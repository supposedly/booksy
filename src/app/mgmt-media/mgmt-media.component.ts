import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { PermsComponent } from '../attrs/perms.component';
import { LocksComponent } from '../attrs/locks.component';
import { MaxesComponent } from '../attrs/maxes.component';

import { MediaTypeService } from '../media-type.service';
import { LocationService } from '../location.service';

import { Globals } from '../globals';

/* -------------------------------------- */
//The 'router wrap' (just holds the menu) //
/* -------------------------------------- */

@Component({
  selector: 'app-mgmt-media',
  template: `
    <div id="container">
      <div id="spacer"></div>
      <generic-header [buttons]="buttons"></generic-header>
      <router-outlet></router-outlet>
    </div>
  `,
  styleUrls: ['./mgmt-media.component.css']
})
export class MgmtMediaComponent {
  buttons = [
    {text: 'search & list', dest: 'list'},
    {text: 'media types', dest: 'types'},
    {text: 'genres'}
  ]
}

/* -------------------------------------- */
// The searchbar/list component at /list  //
/* -------------------------------------- */

@Component({
  selector: 'app-mgmt-media-list',
  template: `
    <button routerLink="../../edit/new">Add item</button>
    <media-search-bar default="all" [level]="3" with-delete></media-search-bar>
  `,
  styles: [''],
})
export class MgmtMediaListComponent {}

/* -------------------------------------- */
// The genre list component at /genres    //
/* -------------------------------------- */

@Component({
  selector: 'app-mgmt-media-genres',
  template: '',
  styles: ['']
})
export class MgmtMediaGenresComponent {
  //just show genres, probably no maxes -- just allow add & delete.
}
