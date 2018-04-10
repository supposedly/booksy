import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { PermsComponent } from '../attrs/perms.component';
import { LocksComponent } from '../attrs/locks.component';
import { LimitsComponent } from '../attrs/limits.component';

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
    <button routerLink="../../edit/new">Add item</button> <whatsthis [ident]="8"></whatsthis>
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
  template: `
    <p>To create a new genre, simply write it into the "new genre" box when adding or editing an item.</p>
    <p *ngIf="msg">{{msg}}</p>
    <ul>
      <li *ngFor="let genre of globals.locGenres; let i = index">
        <span class="container">
          <span class="name">{{genre}}</span>
          <span class="del" (click)="rm(i)">Ⓧ</span>
          &nbsp;
          <span class="editbutton" (click)="isBeingEdited[i]=true"></span>
        </span>
        <span *ngIf="isBeingEdited[i]">
          <input
            type="text"
            (keyup.enter)="edit(i)"
            [value]="globals.locGenres[i]"
            [(ngModel)]="intermediateNames[i]"
          >
          <span class="save" *ngIf="intermediateNames[i]" (click)="edit(i)">✔</span>
        </span>
      </li>
    </ul>
  `,
  styleUrls: ['./mgmt-media-genres.component.css'],
})
export class MgmtMediaGenresComponent {
  msg: string = '';
  isBeingEdited: boolean[];
  intermediateNames: string[];
  
  constructor(
    public globals: Globals,
    private locationService: LocationService
  ) {
    this.isBeingEdited = Array.from({length: globals.locGenres.length}, _ => false);
    this.intermediateNames = Array.from({length: globals.locGenres.length}, _ => null);
    // or Array(globals.locGenres.length).fill(false or null)
  }
  
  edit(i) {
    this.locationService.editGenre(this.globals.locGenres[i], this.intermediateNames[i])
      .subscribe(
        resp => {
          this.globals.locGenres[i] = this.intermediateNames[i];
          this.isBeingEdited[i] = false;
          this.intermediateNames[i] = '';
        },
        err => this.msg = err.error?err.error:'Error.'
      )
  }
    
  rm(i) {
    this.locationService.removeGenre(this.globals.locGenres[i])
      .subscribe(
        resp => this.globals.locGenres.splice(i, 1),
        err => this.msg = err.error?err.error:'Error.'
      )
  }
  
}
