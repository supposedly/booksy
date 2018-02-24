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
//The media-type list component at /types //
/* -------------------------------------- */

@Component({
  selector: 'app-mgmt-media-types',
  template: `
    <button routerLink="./new">New type</button>
    <p *ngIf="msg">{{msg}}</p>
    <ul>
      <li *ngFor="let mtype of globals.locMediaTypes; let i = index" routerLink="./{{mtype.name}}">
        {{mtype.name}}
        <span (click)="deleteType(mtype.name, i)">Ⓧ</span>
      </li>
    </ul>
  `,
  styleUrls: ['./mgmt-media-types.component.css'],
})
export class MgmtMediaTypesComponent {
  mtypes: any = [];
  msg: string = '';
  
  constructor(
    public globals: Globals,
    private mTypeService: MediaTypeService
  ) {}
  
  deleteType(name, i) {
    this.mTypeService.delete(name)
      .subscribe();
    this.globals.locMediaTypes.splice(i, 1);
  }
}

@Component({
  selector: 'app-media-type-detail',
  template: `
  <p>{{msg}}</p>
  <button (click)="location.back()">Go back</button>
  <h2>{{name}}</h2>
  <input type="text" [value]="name" [(ngModel)]="name"/>
  <form name="media-type-information" (ngSubmit)="submit()">
     <app-maxes [arr]="maxArr"></app-maxes>
     <input type="submit" value="Submit"/>
  </form>
  `,
  styles: ['']
})
export class MediaTypeDetailComponent implements OnInit {
  maxArr: any = [];
  initialName: string;
  name: string;
  msg: string = '';
  
  @ViewChild(MaxesComponent) private maxes: MaxesComponent;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private route: ActivatedRoute,
    private mTypeService: MediaTypeService
  ) {}
  
  ngOnInit() {
    this.initialName = this.name = this.route.snapshot.paramMap.get('name');
    if (this.initialName == 'new') {
      this.name = '';
      this.maxArr = null;
    } else {
      this.getInfo();
    }
  }
  
  getInfo() {
    this.mTypeService.info(this.name)
      .subscribe(resp => this.maxArr = resp.props.maxes);
  }
  
  submit() {
    if (this.initialName == 'new') {
      this.mTypeService.add(this.name, this.maxes.arr.names)
        .subscribe(_ => {this.initialName = this.name; this.msg = "Successfully created."}, err => this.msg = err.error?err.error:"Not allowed!")
      this.globals.locMediaTypes.push(this.name); // add to global list of media types as well
    } else {
      this.mTypeService.edit(this.initialName, this.maxes.arr.names, this.name)
        .subscribe(
          _ => this.msg = "Successfully edited.",
          err => this.msg = err.error?err.error:"Not allowed!",
          () => this.mTypeService.all() // refresh global list of media types
                  .subscribe(res => this.globals.locMediaTypes = res.types.map((_, d) => d.name))
        );
    }
  }
}
